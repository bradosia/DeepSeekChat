#include "MainWindow.h"
#include "ui_MainWindow.h"
#include <QProcess>
#include <QTextEdit>
#include <QLineEdit>
#include <QPushButton>
#include <QComboBox>
#include <QTimer>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QTextStream>
#include <QMessageBox>
#include <QDateTime>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , debateTimer(new QTimer(this))
    , pythonProcess(new QProcess(this))
    , topicProcess(new QProcess(this))
    , debateActive(false)
    , currentSpeaker(0)
    , debateRound(0)
{
    ui->setupUi(this);

    // Connect UI elements
    connect(ui->sendButton, &QPushButton::clicked, this, &MainWindow::onSendClicked);
    connect(ui->questionInput, &QLineEdit::returnPressed, this, &MainWindow::onQuestionInputReturnPressed);
    connect(ui->startButton, &QPushButton::clicked, this, &MainWindow::onStartDebateClicked);
    connect(ui->generateTopicButton, &QPushButton::clicked, this, &MainWindow::onGenerateTopicClicked);
    connect(ui->toggleDebugButton, &QPushButton::clicked, this, &MainWindow::onToggleDebugClicked);
    
    // Connect timer and process
    connect(debateTimer, &QTimer::timeout, this, &MainWindow::onDebateTimerTimeout);
    connect(pythonProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &MainWindow::onPythonProcessFinished);
    connect(topicProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &MainWindow::onTopicGenerationFinished);
    
    // Initialize speakers
    initializeSpeakers();
    
    // Set timer interval (3-5 seconds between responses)
    debateTimer->setInterval(4000);
    
    // Set emojis and styling programmatically
    ui->titleLabel->setText("🎙️ Bright Minds Discussion");
    ui->userLabel->setText("👤 User: Aleksander");
    ui->startButton->setText("🎬 Start Debate");
    ui->topicLabel->setText("📝 Topic:");
    ui->sendButton->setText("➤ Send");
    
    // Initialize generate topic button text
    ui->generateTopicButton->setText("🎲 Generate Topic");
    
    // Initialize debug panel
    debugPanelVisible = true;
    
    // Generate initial topic when app opens
    generateInitialTopic();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::initializeSpeakers()
{
    // Load speakers from JSON file
    QFile file("speakers.json");
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::warning(this, "Warning", "Could not load speakers.json");
        logToAudience("❌ Error: Could not load speakers.json", "red");
        return;
    }
    
    QByteArray data = file.readAll();
    QJsonDocument doc = QJsonDocument::fromJson(data);
    QJsonObject root = doc.object();
    QJsonArray speakers = root["speakers"].toArray();
    
    logToAudience("📋 Loading speakers from speakers.json...", "blue");
    
    // Populate combo boxes
    for (const QJsonValue& value : speakers) {
        QJsonObject speaker = value.toObject();
        QString name = speaker["name"].toString();
        
        ui->speaker1ComboBox->addItem(name);
        ui->speaker2ComboBox->addItem(name);
        
        // Store speaker configuration
        SpeakerConfig config;
        config.name = name;
        config.description = speaker["description"].toString();
        config.style = speaker["style"].toString();
        config.temperature = speaker["temperature"].toDouble();
        
        QJsonArray traits = speaker["traits"].toArray();
        for (const QJsonValue& trait : traits) {
            config.traits.append(trait.toString());
        }
        
        speakerConfigs[name] = config;
        
        // Log each speaker loaded
        logToAudience(QString("✅ Loaded: %1 (%2)").arg(name, speaker["description"].toString()), "green");
    }
    
    // Set default selections
    if (ui->speaker1ComboBox->count() > 0) {
        ui->speaker1ComboBox->setCurrentIndex(0);
    }
    if (ui->speaker2ComboBox->count() > 1) {
        ui->speaker2ComboBox->setCurrentIndex(1);
    }
    
    // Show success message with speaker counts
    int totalSpeakers = ui->speaker1ComboBox->count();
    logToAudience(QString("🎉 Successfully loaded %1 speakers into both comboboxes!").arg(totalSpeakers), "green");
    logToAudience("💡 Select two different speakers and enter a topic to start debating.", "blue");
}

void MainWindow::onStartDebateClicked()
{
    if (debateActive) {
        // Stop debate
        debateActive = false;
        debateTimer->stop();
        ui->startButton->setText("🎬 Start Debate");
        ui->startButton->setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;");
        logToAudience("Debate ended.", "red");
        return;
    }
    
    // Get speaker names and topic
    speaker1Name = ui->speaker1ComboBox->currentText();
    speaker2Name = ui->speaker2ComboBox->currentText();
    currentTopic = ui->topicInput->text().trimmed();
    
    if (speaker1Name.isEmpty() || speaker2Name.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please select both speakers.");
        return;
    }
    
    if (currentTopic.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please enter a debate topic.");
        return;
    }
    
    if (speaker1Name == speaker2Name) {
        QMessageBox::warning(this, "Warning", "Please select different speakers.");
        return;
    }
    
    // Start debate
    startDebate();
}

void MainWindow::startDebate()
{
    // Clear previous content
    ui->unifiedChat->clear();
    debateHistory.clear();
    
    // Update UI
    debateActive = true;
    currentSpeaker = 0;
    debateRound = 0;
    ui->startButton->setText("⏹️ Stop Debate");
    ui->startButton->setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;");
    
    // Speaker labels are now handled in the chat messages themselves
    
    // Log debate start
    logToAudience(QString("🎬 Debate started: %1 vs %2 on '%3'").arg(speaker1Name, speaker2Name, currentTopic), "green");
    
    // Start the debate timer
    debateTimer->start();
}

void MainWindow::onDebateTimerTimeout()
{
    if (!debateActive) return;
    
    continueDebate();
}

void MainWindow::continueDebate()
{
    if (!pythonProcess) {
        logToAudience("Error: Python process not initialized", "red");
        return;
    }
    
    QString currentSpeakerName = (currentSpeaker == 0) ? speaker1Name : speaker2Name;
    
    // Build context from debate history
    QString context = debateHistory.join("\n");
    
    // Prepare Python process arguments
    QStringList arguments;
    arguments << "python_interface.py" 
             << currentSpeakerName 
             << currentTopic 
             << context 
             << ""  // No user question
             << "true";  // Is debate continuation
    
    // Start Python process
    pythonProcess->start("python", arguments);
    
    // Connect stderr to handle debug output
    connect(pythonProcess, &QProcess::readyReadStandardError, this, &MainWindow::onPythonProcessError);
}

void MainWindow::onPythonProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    if (!pythonProcess) {
        logToAudience("Error: Python process not available", "red");
        return;
    }
    
    if (exitCode != 0) {
        logToAudience(QString("Error: Python process failed with exit code %1").arg(exitCode), "red");
        QString errorOutput = pythonProcess->readAllStandardError();
        if (!errorOutput.isEmpty()) {
            logToAudience(QString("Python error: %1").arg(errorOutput), "red");
        }
        return;
    }
    
    QString output = pythonProcess->readAllStandardOutput().trimmed();
    if (output.isEmpty()) {
        logToAudience("Error: No response from AI", "red");
        return;
    }
    
    // Send message to current speaker
    QString currentSpeakerName = (currentSpeaker == 0) ? speaker1Name : speaker2Name;
    
    // Only add to debate history if it's a valid response
    if (!output.contains("Debug:") && 
        output.trimmed() != "None" && 
        output.trimmed() != "No valid response generated" &&
        !output.trimmed().isEmpty() &&
        !output.contains("Using fallback response")) {
        sendSpeakerMessage(currentSpeakerName, output);
        // Add to debate history
        debateHistory.append(QString("%1: %2").arg(currentSpeakerName, output));
    } else if (output.contains("Using fallback response")) {
        // Extract the fallback response and log the API failure
        QStringList lines = output.split('\n');
        QString failureReason = "Unknown";
        
        // Find the API failure reason
        for (const QString& line : lines) {
            if (line.contains("API_FAILED:")) {
                failureReason = line.split(":").last().trimmed();
                break;
            }
        }
        
        // Log the API failure
        logToAudience(QString("⚠️ API failed for %1 (%2) - using fallback response").arg(currentSpeakerName, failureReason), "orange");
        
        // Extract and use the fallback response
        for (const QString& line : lines) {
            if (!line.contains("Debug:") && 
                !line.contains("Using fallback response") &&
                !line.contains("API_FAILED:") &&
                !line.trimmed().isEmpty() &&
                line.trimmed() != "None") {
                sendSpeakerMessage(currentSpeakerName, line.trimmed());
                debateHistory.append(QString("%1: %2").arg(currentSpeakerName, line.trimmed()));
                break;
            }
        }
    // Note: Debug information is now handled separately via stderr reading
    } else if (output.contains("Debug: API call failed") || output.contains("Debug: Invalid API response") || output.contains("Debug: API returned invalid content")) {
        // Topic generation failed
        logToAudience("⚠️ Topic generation API failed - using fallback topic", "orange");
        
        // Extract the fallback topic
        QStringList lines = output.split('\n');
        for (const QString& line : lines) {
            if (!line.contains("Debug:") && 
                !line.trimmed().isEmpty() &&
                line.trimmed() != "None") {
                ui->topicInput->setText(line.trimmed());
                break;
            }
        }
    } else {
        logToAudience(QString("⚠️ Skipping invalid response from %1").arg(currentSpeakerName), "orange");
    }
    
    // Switch to next speaker
    currentSpeaker = (currentSpeaker == 0) ? 1 : 0;
    debateRound++;
    
    // Check if debate should continue (max 20 rounds = ~10 minutes)
    if (debateRound >= 20) {
        debateActive = false;
        debateTimer->stop();
        ui->startButton->setText("🎬 Start Debate");
        ui->startButton->setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;");
        logToAudience("Debate concluded after maximum rounds.", "blue");
    }
}

void MainWindow::onPythonProcessError()
{
    if (!pythonProcess) return;
    
    QString errorOutput = pythonProcess->readAllStandardError();
    QStringList lines = errorOutput.split('\n');
    
    for (const QString& line : lines) {
        if (line.contains("🔍") || line.contains("URL:") || line.contains("Headers:") || 
            line.contains("Payload:") || line.contains("API Key:") || line.contains("Status Code:") || 
            line.contains("Response Headers:") || line.contains("Response Text:")) {
            logToAudience(line.trimmed(), "orange");
        }
    }
}

void MainWindow::generateInitialTopic()
{
    if (!topicProcess) {
        logToAudience("Error: Topic process not available", "red");
        return;
    }
    
    // Log that we're generating initial topic
    logToAudience("🎲 Generating initial topic...", "blue");
    
    // Prepare Python process arguments for topic generation
    QStringList arguments;
    arguments << "python_interface.py" 
             << "topic_generator" 
             << ""  // No topic needed for generation
             << ""  // No context
             << ""  // No user question
             << "false";  // Not debate continuation
    
    // Start topic generation process
    topicProcess->start("python", arguments);
}

void MainWindow::onSendClicked()
{
    if (!debateActive) {
        QMessageBox::information(this, "Info", "Please start a debate first.");
        return;
    }
    
    QString userQuestion = ui->questionInput->text().trimmed();
    if (userQuestion.isEmpty()) return;
    
    // Log user question
    logToAudience(QString("❓ Audience Question: %1").arg(userQuestion), "orange");
    
    // Build context from debate history
    QString context = debateHistory.join("\n");
    
    // Send question to both speakers
    QStringList speakers = {speaker1Name, speaker2Name};
    for (const QString& speaker : speakers) {
        // Prepare Python process arguments for user question
        QStringList arguments;
        arguments << "python_interface.py" 
                 << speaker 
                 << currentTopic 
                 << context 
                 << userQuestion 
                 << "false";  // Not debate continuation
        
        // Create a new process for each speaker
        QProcess* process = new QProcess(this);
        connect(process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
                [this, process, speaker](int exitCode, QProcess::ExitStatus exitStatus) {
            if (exitCode == 0) {
                QString output = process->readAllStandardOutput().trimmed();
                if (!output.isEmpty()) {
                    sendSpeakerMessage(speaker, output);
                }
            }
            process->deleteLater();
        });
        
        process->start("python", arguments);
    }
    
    // Clear input
    ui->questionInput->clear();
}

void MainWindow::onQuestionInputReturnPressed()
{
    onSendClicked();
}

void MainWindow::sendSpeakerMessage(const QString& speaker, const QString& message)
{
    // Format message with timestamp
    QDateTime now = QDateTime::currentDateTime();
    QString timestamp = now.toString("HH:mm:ss");
    
    // Determine alignment based on speaker
    QString alignment = (speaker == speaker1Name) ? "left" : "right";
    QString backgroundColor = (speaker == speaker1Name) ? "#e3f2fd" : "#f3e5f5";
    QString borderColor = (speaker == speaker1Name) ? "#2196f3" : "#9c27b0";
    
    // Create Microsoft Teams-style message
    QString formattedMessage = QString(
        "<div style='margin: 8px 0; text-align: %1;'>"
        "<div style='display: inline-block; max-width: 70%%; background-color: %2; border: 1px solid %3; "
        "border-radius: 12px; padding: 8px 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
        "<div style='font-weight: bold; color: %4; font-size: 12px; margin-bottom: 4px;'>%5</div>"
        "<div style='color: #333; line-height: 1.4;'>%6</div>"
        "<div style='font-size: 10px; color: #666; margin-top: 4px;'>%7</div>"
        "</div></div>"
    ).arg(alignment, backgroundColor, borderColor, borderColor, speaker, message, timestamp);
    
    ui->unifiedChat->append(formattedMessage);
    
    // Scroll to bottom
    QTextCursor cursor = ui->unifiedChat->textCursor();
    cursor.movePosition(QTextCursor::End);
    ui->unifiedChat->setTextCursor(cursor);
}

void MainWindow::logToAudience(const QString& message, const QString& color)
{
    QDateTime now = QDateTime::currentDateTime();
    QString timestamp = now.toString("HH:mm:ss");
    
    // Check if this is a debug-only message that should only go to debug panel
    bool debugOnly = message.contains("🔍") || 
                     message.contains("URL:") || 
                     message.contains("Headers:") || 
                     message.contains("Payload:") || 
                     message.contains("Status Code:") || 
                     message.contains("Response Headers:") || 
                     message.contains("Response Text:") ||
                     message.contains("API Key:") ||
                     message.contains("📋 Loading speakers") ||
                     message.contains("✅ Loaded:") ||
                     message.contains("🎉 Successfully loaded") ||
                     message.contains("🎲 Generating initial topic") ||
                     message.contains("🎲 Generating debate topic");
    
    // Only show in main chat if it's not a debug-only message
    if (!debugOnly) {
        // Create centered audience message
        QString formattedMessage = QString(
            "<div style='margin: 8px 0; text-align: center;'>"
            "<div style='display: inline-block; max-width: 80%%; background-color: #f8f9fa; border: 1px solid #dee2e6; "
            "border-radius: 12px; padding: 8px 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
            "<div style='font-weight: bold; color: #6c757d; font-size: 12px; margin-bottom: 4px;'>👥 Audience</div>"
            "<div style='color: %1; line-height: 1.4;'>%2</div>"
            "<div style='font-size: 10px; color: #666; margin-top: 4px;'>%3</div>"
            "</div></div>"
        ).arg(color, message, timestamp);
        
        ui->unifiedChat->append(formattedMessage);
        
        // Scroll to bottom
        QTextCursor cursor = ui->unifiedChat->textCursor();
        cursor.movePosition(QTextCursor::End);
        ui->unifiedChat->setTextCursor(cursor);
    }
    
    // Always log to debug panel if it's any kind of debug message
    if (debugOnly || message.contains("Debug:") || message.contains("API") || message.contains("⚠️")) {
        QString debugMessage = QString("[%1] %2").arg(timestamp, message);
        ui->debugLog->append(debugMessage);
        
        // Scroll debug log to bottom
        QTextCursor debugCursor = ui->debugLog->textCursor();
        debugCursor.movePosition(QTextCursor::End);
        ui->debugLog->setTextCursor(debugCursor);
    }
}

void MainWindow::onGenerateTopicClicked()
{
    if (!topicProcess) {
        logToAudience("Error: Topic process not initialized", "red");
        return;
    }
    
    logToAudience("🎲 Generating debate topic...", "blue");
    
    // Prepare Python process arguments for topic generation
    QStringList arguments;
    arguments << "python_interface.py" 
             << "topic_generator" 
             << "debate_topic" 
             << "" 
             << "" 
             << "false";
    
    // Start topic generation process
    topicProcess->start("python", arguments);
}

void MainWindow::onTopicGenerationFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    if (!topicProcess) {
        logToAudience("Error: Topic process not available", "red");
        return;
    }
    
    if (exitCode != 0) {
        logToAudience("Error: Topic generation failed", "red");
        QString errorOutput = topicProcess->readAllStandardError();
        if (!errorOutput.isEmpty()) {
            logToAudience(QString("Python error: %1").arg(errorOutput), "red");
        }
        return;
    }
    
    QString output = topicProcess->readAllStandardOutput().trimmed();
    if (!output.isEmpty() && !output.contains("Debug:") && output.trimmed() != "No valid response generated") {
        ui->topicInput->setText(output);
        logToAudience(QString("🎯 Generated topic: %1").arg(output), "green");
    } else {
        logToAudience("Error: Could not generate topic", "red");
    }
}



void MainWindow::onToggleDebugClicked()
{
    debugPanelVisible = !debugPanelVisible;
    
    if (debugPanelVisible) {
        ui->debugPanel->setVisible(true);
        ui->toggleDebugButton->setText("−");
        ui->toggleDebugButton->setToolTip("Minimize Debug Panel");
    } else {
        ui->debugPanel->setVisible(false);
        ui->toggleDebugButton->setText("+");
        ui->toggleDebugButton->setToolTip("Expand Debug Panel");
    }
}

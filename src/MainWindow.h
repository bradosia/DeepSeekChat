#pragma once

#include <QMainWindow>
#include <QTimer>
#include <QProcess>
#include <QStringList>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onSendClicked();
    void onQuestionInputReturnPressed();
    void onStartDebateClicked();
    void onDebateTimerTimeout();
    void onPythonProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onPythonProcessError();
    void onGenerateTopicClicked();
    void generateInitialTopic();
    void onTopicGenerationFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void onToggleDebugClicked();

private:
    void initializeSpeakers();
    void startDebate();
    void continueDebate();
    void sendSpeakerMessage(const QString& speaker, const QString& message);
    void logToAudience(const QString& message, const QString& color = "black");
    QString getSpeakerPrompt(const QString& speaker, const QString& context, const QString& topic, bool isUserQuestion = false);
    
    Ui::MainWindow *ui;
    QTimer *debateTimer;
    QProcess *pythonProcess;
    QProcess *topicProcess;
    
    // Debate state
    bool debateActive;
    int currentSpeaker; // 0 = speaker1, 1 = speaker2
    int debateRound;
    QString speaker1Name;
    QString speaker2Name;
    QString currentTopic;
    QStringList debateHistory;
    
    // Speaker configurations
    struct SpeakerConfig {
        QString name;
        QString description;
        QString style;
        QStringList traits;
        double temperature;
    };
    
    QMap<QString, SpeakerConfig> speakerConfigs;
    
    // Debug panel state
    bool debugPanelVisible;
};

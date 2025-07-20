#include "MainWindow.h"
#include "ui_MainWindow.h"
#include <QProcess>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    connect(ui->sendButton, &QPushButton::clicked, this, &MainWindow::onSendClicked);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::onSendClicked()
{
    QString userInput = ui->inputBox->text();
    ui->chatDisplay->append("You: " + userInput);

    QProcess *process = new QProcess(this);
    QStringList arguments;
    arguments << "python_interface.py" << userInput;

    connect(process, &QProcess::readyReadStandardOutput, [=]() {
        QString output = process->readAllStandardOutput();
        ui->chatDisplay->append("AI: " + output.trimmed());
    });

    process->start("python", arguments);
}

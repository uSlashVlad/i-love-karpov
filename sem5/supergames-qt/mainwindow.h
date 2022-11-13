#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include "sguser.h"
#include "sgdeveloper.h"
#include "databasecontainer.h"
#include <QMainWindow>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow, private DatabaseContainer
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void on_connectionButton_clicked();

    void on_radioButtonUser_clicked();

    void on_radioButtonGuest_clicked();

    void on_radioButtonDeveloper_clicked();

    void on_registerPushButton_clicked();

    void on_loginPushButton_clicked();

    void on_loginField_returnPressed();

    void on_passwordField_returnPressed();

private:
    Ui::MainWindow *ui;

    SgUser loginAsUser(QString login, QString password, bool &ok);
    SgDeveloper loginAsDeveloper(QString login, QString password, bool &ok);
};
#endif // MAINWINDOW_H

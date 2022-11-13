#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "connectiondialog.h"
#include "registerdialog.h"
#include "storewindow.h"
#include "commonpatterns.h"
#include "dialoghelper.h"
#include "hash.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      DatabaseContainer(parent),
      ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}


void MainWindow::on_connectionButton_clicked()
{
    auto newConnection = new QSqlDatabase(QSqlDatabase::addDatabase("QPSQL"));
    auto isSaved = new bool(false);
    auto connectionDialog = ConnectionDialog(newConnection, isSaved, this);
    // Открываю
    connectionDialog.exec();

    // Исполнится, когда закроется
    if (*isSaved) {
        if (mainDatabase != nullptr) {
            if (mainDatabase->isOpen()) mainDatabase->close();
            delete mainDatabase;
        }

        mainDatabase = newConnection;

        ui->signInBlock->setEnabled(true);
    }

    delete isSaved;
}


void MainWindow::on_radioButtonGuest_clicked()
{
    ui->formFrame->setEnabled(false);
}

void MainWindow::on_radioButtonUser_clicked()
{
    ui->formFrame->setEnabled(true);
    ui->loginLabel->setText("Логин:");
}

void MainWindow::on_radioButtonDeveloper_clicked()
{
    ui->formFrame->setEnabled(true);
    ui->loginLabel->setText("Почта:");
}


void MainWindow::on_loginPushButton_clicked()
{
    if (ui->radioButtonGuest->isChecked()) {
        auto window = new StoreWindow(SgUser(0, "_guest", "", "Гость", QDateTime::currentDateTime()), mainDatabase);
        window->show();
    } else {
        auto isUser = ui->radioButtonUser->isChecked();

        auto login = ui->loginField->text().trimmed();
        if (isUser) {
            if (!login.contains(CommonPatterns::loginRegex)) {
                DialogHelper::showValidationError(this, "Неверный логин");
                return;
            }
        } else {
            if (!login.contains(CommonPatterns::emailRegex)) {
                DialogHelper::showValidationError(this, "Неверная почта");
                return;
            }
        }

        auto password = ui->passwordField->text().trimmed();
        if (password.isEmpty()) {
            DialogHelper::showValidationError(this, "Пароль не может быть пустым");
            return;
        }

        if (isUser) {
            bool ok;
            auto user = loginAsUser(login, password, ok);

            if (!ok) {
                DialogHelper::showAuthError(this, isUser);
                return;
            }

            auto window = new StoreWindow(user, mainDatabase);
            window->show();
        }
    }
}

SgUser MainWindow::loginAsUser(QString login, QString password, bool &ok)
{
    SgUser user;

    if (!checkDatabase()) {
        ok = false;
        return user;
    }

    auto hashedPassword = hashString(password);

    auto query = QString("SELECT * FROM users WHERE login = '%1' AND \"password\" = '%2'")
            .arg(login, hashedPassword);
    auto q = mainDatabase->exec(query);
    if (q.size() < 1) {
        ok = false;
        return user;
    }
    q.first();

    if (DialogHelper::isSqlError(q.lastError())) {
        DialogHelper::showSqlError(this, q.lastError(), query);
        ok = false;
        return user;
    }

    user.id = q.value(0).toInt();
    user.login = q.value(1).toString();
    user.password = q.value(2).toString();
    user.name = q.value(3).toString();
    user.date = q.value(4).toDateTime();

    ok = true;
    return user;
}

SgDeveloper MainWindow::loginAsDeveloper(QString login, QString password, bool &ok)
{
    SgDeveloper dev;

    if (!checkDatabase()) {
        ok = false;
        return dev;
    }

    auto hashedPassword = hashString(password);

    auto query = QString("SELECT * FROM developers WHERE email = '%1' AND \"password\" = '%2'")
            .arg(login, hashedPassword);
    auto q = mainDatabase->exec(query);
    if (DialogHelper::isSqlError(q.lastError())) {
        DialogHelper::showSqlError(this, q.lastError(), query);
        ok = false;
        return dev;
    }

    dev.id = q.value(0).toInt();

    ok = true;
    return dev;
}

void MainWindow::on_registerPushButton_clicked()
{
    auto registerDialog = RegisterDialog(mainDatabase, this);
    registerDialog.exec();
}


void MainWindow::on_loginField_returnPressed()
{
    focusNextChild();
}

void MainWindow::on_passwordField_returnPressed()
{
    on_loginPushButton_clicked();
}

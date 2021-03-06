#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <passwords.h>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:

    void on_pushButtonAdd_clicked();

    void deleteButtonClick();

    void on_tableWidget_cellChanged(int row, int column);

private:
    Ui::MainWindow *ui;

    Passwords passwords;
};
#endif // MAINWINDOW_H

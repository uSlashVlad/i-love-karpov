#ifndef REVIEWDIALOG_H
#define REVIEWDIALOG_H

#include <QDialog>

namespace Ui {
class ReviewDialog;
}

class ReviewDialog : public QDialog
{
    Q_OBJECT

public:
    explicit ReviewDialog(QWidget *parent = nullptr);
    ~ReviewDialog();

private:
    Ui::ReviewDialog *ui;
};

#endif // REVIEWDIALOG_H

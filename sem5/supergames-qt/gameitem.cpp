#include "gameitem.h"
#include "ui_gameitem.h"

GameItem::GameItem(int id, QString name, QString description, QString developer, double price, QWidget *parent)
    : QWidget(parent),
      ui(new Ui::GameItem),
      id(id)/*,
      name(name),
      description(description),
      developer(developer),
      price(price)*/
{
    ui->setupUi(this);

    ui->gameTitle->setText(name);
    ui->gameDescription->setText(description);
    ui->gameDeveloper->setText(developer);
    ui->priceLabel->setText(QString::number(price) + " руб.");
}

GameItem::~GameItem()
{
    delete ui;
}

void GameItem::on_buyButton_clicked()
{
    emit onGameButtonPressed(id);
}

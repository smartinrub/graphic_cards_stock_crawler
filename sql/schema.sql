CREATE DATABASE IF NOT EXISTS graphic_cards_stock_crawler CHARACTER SET utf8 COLLATE utf8_general_ci;

USE graphic_cards_stock_crawler;

CREATE TABLE IF NOT EXISTS graphic_card (
	model VARCHAR(256) PRIMARY KEY,
   	max_price DECIMAL(6,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS stock (
	name VARCHAR(256) PRIMARY KEY,
	model VARCHAR(256) REFERENCES graphic_card(model),
   	price DECIMAL(6,2) NOT NULL,
	in_stock_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

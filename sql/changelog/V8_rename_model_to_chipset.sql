USE graphic_cards_stock_crawler;
ALTER TABLE graphic_card CHANGE COLUMN model chipset VARCHAR(256);
ALTER TABLE stock CHANGE COLUMN model chipset VARCHAR(256);

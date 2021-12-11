USE graphic_cards_stock_crawler;
ALTER TABLE graphic_card RENAME COLUMN model TO chipset;
ALTER TABLE stock RENAME COLUMN model TO chipset;

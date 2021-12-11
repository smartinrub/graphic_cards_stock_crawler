USE graphic_cards_stock_crawler;
ALTER TABLE stock MODIFY in_stock_date DATETIME DEFAULT CURRENT_TIMESTAMP;

USE graphic_cards_stock_crawler;
ALTER TABLE stock ADD CONSTRAINT FK_GraphicCardStock FOREIGN KEY (chipset) REFERENCES graphic_card(chipset);

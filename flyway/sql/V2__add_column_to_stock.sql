ALTER TABLE stock DROP PRIMARY KEY;
ALTER TABLE stock ADD id VARCHAR(255) DEFAULT (uuid()) PRIMARY KEY FIRST;
UPDATE stock SET id = uuid() WHERE id IS NULL;
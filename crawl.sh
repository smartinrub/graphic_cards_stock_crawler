#!/bin/sh
# add random delay to mimic user behaviour
sleep $((RANDOM % 10))
# go to the spider directory
cd /home/pi/scrapy-projects/graphic_cards_stock_crawler
# run the spider
/usr/local/bin/scrapy crawl graphic_cards_stock

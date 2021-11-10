import logging

import scrapy
from telegram.parsemode import ParseMode
from telegram.utils.helpers import escape_markdown

from . import db
from . import telegram

base_url = 'https://www.coolmod.com'
telegram_chat_id = "1652193495"


class GraphicCardsSpider(scrapy.Spider):
    name = "graphic_cards"
    start_urls = [
        f'{base_url}/tarjetas-graficas/',
    ]

    def parse(self, response, **kwargs):
        processed_cards = []
        target_cards = self.find_all_graphic_cards()

        for graphic_card in response.selector.xpath(
                '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div'):
            name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
            link = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
            price = graphic_card.xpath(
                'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"]/text())')[
                0].extract()

            result = self.find_stock(name)

            if result[0][0] != 0:
                logging.info(f"Skipping: [{name}]. Already notified.")
                continue

            # skip if the card was already processed
            if name in processed_cards:
                logging.info(f"Skipping: [{name}]. Already processed.")
                continue

            processed_cards.append(name)

            for target_card in target_cards:
                if target_card['model'] in name and target_card['max_price'] >= self.parse_price(price):
                    self.send_message(name, target_card['model'], price, link)
                    self.add_stock(name, target_card['model'], self.parse_price(price))

        db.get_sql_connector().close()

    @staticmethod
    def parse_price(price: str):
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

    @staticmethod
    def send_message(name: str, model: str, price: str, link: str):
        message = """
        📣 *{0}*
        📃 Model: *{1}* 
        💰 Price: *{2}* 
        🌎 Link: *[BUY]({3})*
                                """.format(
            escape_markdown(name, 2),
            escape_markdown(model, 2),
            escape_markdown(price, 2),
            base_url + link
        )

        telegram.get_bot().send_message(text=message, chat_id=telegram_chat_id, parse_mode=ParseMode.MARKDOWN_V2)

    @staticmethod
    def find_all_graphic_cards() -> list:
        cur = db.get_sql_connector().cursor(dictionary=True)
        cur.execute("SELECT * FROM graphic_card")
        return cur.fetchall()

    @staticmethod
    def find_stock(name: str) -> list:
        cur = db.get_sql_connector().cursor()
        query = f"SELECT COUNT(*) FROM stock WHERE name='{name}'"
        cur.execute(query)
        return cur.fetchall()

    @staticmethod
    def add_stock(name: str, model: str, price: float):
        cur = db.get_sql_connector().cursor()
        query = f"INSERT INTO stock (name, model, price) VALUES ('{name}', '{model}', '{price}')"
        cur.execute(query)
        db.get_sql_connector().commit()

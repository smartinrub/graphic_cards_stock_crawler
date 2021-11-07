import os

import scrapy
import telegram
from telegram.parsemode import ParseMode
from telegram.utils.helpers import escape_markdown

from . import db

base_url = 'https://www.coolmod.com'

target_cards: list = [
    {
        "name": "3060",
        "max_price": 450,
        "exclusions": ["3060 Ti"]
    },
    {
        "name": "3060 Ti",
        "max_price": 650,
        "exclusions": []
    },
    {
        "name": "3070",
        "max_price": 700,
        "exclusions": ["3070 Ti"]
    },
    {
        "name": "3070 Ti",
        "max_price": 1000,
        "exclusions": []
    },
    {
        "name": "3080",
        "max_price": 1100,
        "exclusions": ["3080 Ti"]
    },
    {
        "name": "3080 Ti",
        "max_price": 1400,
        "exclusions": []
    },
    {
        "name": "3090",
        "max_price": 1800,
        "exclusions": ["3090 Ti"]
    },
]

telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = "1652193495"


class GraphicCardsSpider(scrapy.Spider):
    name = "graphic_cards"
    start_urls = [
        f'{base_url}/tarjetas-graficas/',
    ]

    def parse(self, response, **kwargs):
        bot = telegram.Bot(token=telegram_token)
        result = []
        for graphic_card in response.selector.xpath(
                '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div'):
            name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
            link = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
            price = graphic_card.xpath(
                'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"]/text())')[
                0].extract()

            for target_card in target_cards:
                if target_card['name'] in name and target_card['max_price'] >= self.parse_price(price):
                    if name not in result:
                        result.append(name)
                        message = """
📣 *{0}*
📃 Model: *{1}* 
💰 Price: *{2}* 
🌎 Link: *[BUY]({3})*
                        """.format(
                            escape_markdown(name, 2),
                            escape_markdown(target_card['name'], 2),
                            escape_markdown(price, 2),
                            base_url + link
                        )
                        bot.send_message(text=message, chat_id=telegram_chat_id, parse_mode=ParseMode.MARKDOWN_V2)

                        cur = db.getSqlConnector().cursor()
                        query = f"INSERT INTO graphic_card (name, price) VALUES ('{name}', '{self.parse_price(price)}')"
                        cur.execute(query)
                        db.getSqlConnector().commit()

        db.getSqlConnector().close()

    @staticmethod
    def parse_price(price: str):
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

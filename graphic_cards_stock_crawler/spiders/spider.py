import datetime
import logging
import uuid
from datetime import datetime, timedelta
from typing import List

import scrapy
from telegram import Bot
from telegram.parsemode import ParseMode
from telegram.utils.helpers import escape_markdown

from graphic_cards_stock_crawler.utils.db import GraphicCard, Stock, DB
from graphic_cards_stock_crawler.utils.telegram_bot import TelegramBot

base_url = 'https://www.coolmod.com'
telegram_chat_id = "1652193495"


class GraphicCardsSpider(scrapy.Spider):
    telegram_bot: TelegramBot
    db: DB

    name = "graphic_cards_stock"
    start_urls = [
        f'{base_url}/tarjetas-graficas/',
    ]

    def parse(self, response, **kwargs):
        self.db = DB()
        self.telegram_bot = TelegramBot()
        processed_cards = []
        target_cards: List[GraphicCard] = self.db.get_all_graphic_cards()

        for graphic_card in response.selector.xpath(
                '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div'):
            name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
            link = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
            price = graphic_card.xpath(
                'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"]/text())')[
                0].extract()

            result: List[Stock] = self.db.get_all_stock_by_name(name)

            # was notified in the last hour
            if len(result) != 0 and result[0].in_stock_date + timedelta(hours=1) > datetime.now():
                logging.info(f"Skipping: [{name}]. Already notified.")
                continue

            # skip if the card was already processed
            if name in processed_cards:
                logging.info(f"Skipping: [{name}]. Already processed.")
                continue

            processed_cards.append(name)

            for target_card in target_cards:
                if target_card.model in name and target_card.max_price >= self.parse_price(price):
                    self.send_message(name, target_card.model, price, link)
                    self.db.add_stock(
                        Stock(id=str(uuid.uuid4()), name=name, model=target_card.model, price=self.parse_price(price)))

    @staticmethod
    def parse_price(price: str):
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

    def send_message(self, name: str, model: str, price: str, link: str):
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

        bot: Bot = self.telegram_bot.get_bot()
        bot.send_message(text=message, chat_id=telegram_chat_id, parse_mode=ParseMode.MARKDOWN_V2)

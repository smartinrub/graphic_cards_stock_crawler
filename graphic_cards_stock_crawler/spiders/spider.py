import datetime
import json
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

coolmod_base_url = 'https://www.coolmod.com'
ldlc_base_url = 'https://www.ldlc.com'
vsgamers_base_url = 'https://www.vsgamers.es'
telegram_chat_id = "1652193495"


class GraphicCardsSpider(scrapy.Spider):
    telegram_bot: TelegramBot = TelegramBot()
    db: DB = DB()

    processed_cards = []

    name = "graphic_cards_stock"
    start_urls = [
        # f'{coolmod_base_url}/tarjetas-graficas/',
        # f'{ldlc_base_url}/es-es/informatica/piezas-de-informatica/tarjeta-grafica/c4684/+fdi-1+fv1026-5801.html',
        f'{vsgamers_base_url}/category/componentes/tarjetas-graficas?hidden_without_stock=true&filter-tipo=nvidia-537'
    ]

    def parse(self, response, **kwargs):
        if "coolmod" in response.url:
            logging.info("Start processing Graphic Cards Stock from COOLMOD.")

            for graphic_card in response.selector.xpath(
                    '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div'):
                name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
                if not name:
                    continue
                path = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
                price = self.parse_price(graphic_card.xpath(
                    'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"])')[
                                             0].extract())
                self.process_graphic_card(name, price, f'{coolmod_base_url}{path}')

        elif "ldlc" in response.url:
            logging.info("Start processing Graphic Cards Stock from LDLC.")
            graphic_cards_in_script = response.xpath('//script')[3].extract()
            first = graphic_cards_in_script.find('{')
            last = graphic_cards_in_script.rfind('}')
            found_graphic_cards_json = json.loads(graphic_cards_in_script[first:last]
                                                  .replace("'", "\"") + "}")['ecommerce']['impressions']

            for graphic_card in response.selector.xpath('//div[@class="listing-product"]/ul/li'):
                id = graphic_card.css('li::attr(id)').extract()[0][4:]
                name = graphic_card.xpath('normalize-space(.//div[@class="pdt-desc"]//a/text())')[0].extract()
                path = graphic_card.xpath('normalize-space(.//div[@class="pdt-desc"]//a/@href)')[0].extract()
                price = float(list(filter(lambda x: x['id'] == id, found_graphic_cards_json))[0].get('price'))
                self.process_graphic_card(name, price, f'{ldlc_base_url}{path}')
        elif "vsgamers" in response.url:
            logging.info("Start processing Graphic Cards Stock from VS Gamers.")

            for graphic_card in response.selector.xpath(
                    '//div[@class="vs-product-list"]/div[@class="vs-product-list-item"]'):
                name = graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-title"])')[0].extract()
                if not name:
                    continue
                path = graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-title"]/a/@href)')[
                    0].extract()
                price = self.parse_price(
                    graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-prices"])')[0].extract())
                self.process_graphic_card(name, price, f'{vsgamers_base_url}{path}')

    def process_graphic_card(self, name: str, price: float, link: str):
        result: List[Stock] = self.db.get_all_stock_by_name(name)

        # was notified in the last hour
        if len(result) != 0 and result[0].in_stock_date + timedelta(hours=1) > datetime.now():
            logging.info(f"Skipping: [{name}]. Already notified.")
            return

        # skip if the card was already processed
        if name in self.processed_cards:
            logging.info(f"Skipping: [{name}]. Already processed.")
            return

        self.processed_cards.append(name)

        target_cards: List[GraphicCard] = self.db.get_all_graphic_cards()
        for target_card in target_cards:  # duplicated entries when series ti and normal
            if target_card.model in name and target_card.max_price >= price:
                self.send_message(name, target_card.model, str(price), link)
                self.db.add_stock(
                    Stock(id=str(uuid.uuid4()), name=name, model=target_card.model, price=price))

    @staticmethod
    def parse_price(price: str) -> float:
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
            link
        )

        bot: Bot = self.telegram_bot.get_bot()
        bot.send_message(text=message, chat_id=telegram_chat_id, parse_mode=ParseMode.MARKDOWN_V2)

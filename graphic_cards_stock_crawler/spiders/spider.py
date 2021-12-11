import json
import logging
import uuid
from typing import List

import scrapy

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
        f'{coolmod_base_url}/tarjetas-graficas/',
        # f'{ldlc_base_url}/es-es/informatica/piezas-de-informatica/tarjeta-grafica/c4684/+fdi-1+fv1026-5801.html',
        f'{vsgamers_base_url}/category/componentes/tarjetas-graficas?hidden_without_stock=true&filter-tipo=nvidia-537'
    ]

    def parse(self, response, **kwargs):
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        if "coolmod" in response.url:
            logging.info("Start processing Graphic Cards Stock from COOLMOD.")

            graphic_cards_found = response.selector.xpath(
                '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div')
            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
                if not name:
                    continue
                path = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
                price = self.parse_price(graphic_card.xpath(
                    'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"])')[
                                             0].extract())
                self.process_graphic_card(name, price, f'{coolmod_base_url}{path}', graphic_card_targets)

        elif "ldlc" in response.url:
            logging.info("Start processing Graphic Cards Stock from LDLC.")
            graphic_cards_in_script = response.xpath('//script')[3].extract()
            first = graphic_cards_in_script.find('{')
            last = graphic_cards_in_script.rfind('}')
            found_graphic_cards_json = json.loads(graphic_cards_in_script[first:last]
                                                  .replace("'", "\"") + "}")['ecommerce']['impressions']

            graphic_cards_found = response.selector.xpath('//div[@class="listing-product"]/ul/li')
            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                item_id = graphic_card.css('li::attr(id)').extract()[0][4:]
                name = graphic_card.xpath('normalize-space(.//div[@class="pdt-desc"]//a/text())')[0].extract()
                path = graphic_card.xpath('normalize-space(.//div[@class="pdt-desc"]//a/@href)')[0].extract()
                price = float(list(filter(lambda x: x['id'] == item_id, found_graphic_cards_json))[0].get('price'))
                self.process_graphic_card(name, price, f'{ldlc_base_url}{path}', graphic_card_targets)

        elif "vsgamers" in response.url:
            logging.info("Start processing Graphic Cards Stock from VS Gamers.")

            graphic_cards_found = response.selector.xpath(
                '//div[@class="vs-product-list"]/div[@class="vs-product-list-item"]')
            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                name = graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-title"])')[0].extract()
                if not name:
                    continue
                path = graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-title"]/a/@href)')[
                    0].extract()
                price = self.parse_price(
                    graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-prices"])')[0].extract())
                self.process_graphic_card(name, price, f'{vsgamers_base_url}{path}', graphic_card_targets)

    def closed(self, reason):
        non_expired_stocks: List[Stock] = self.db.get_non_expired_stock()
        for non_expired_stock in non_expired_stocks:
            if non_expired_stock.name not in self.processed_cards:
                self.telegram_bot.edit_message(
                    chat_id=telegram_chat_id,
                    message_id=non_expired_stock.telegram_message_id,
                    name=non_expired_stock.name,
                    model=non_expired_stock.model,
                    price=str(non_expired_stock.price),
                    link=non_expired_stock.link
                )
                self.db.set_expired_stock(non_expired_stock.name)

    def process_graphic_card(self, name: str, price: float, link: str, graphic_card_targets: list):
        saved_stock: List[Stock] = self.db.get_all_non_expired_stock_by_name(name)

        self.processed_cards.append(name)

        # was notified in the last hour
        if len(saved_stock) != 0:
            logging.info(f"Skipping: [{name}]. Already notified.")
            return

        for target_card in graphic_card_targets:
            if target_card.model in name and target_card.max_price >= price:
                message = self.telegram_bot.send_message(telegram_chat_id, name, target_card.model, str(price), link)
                self.db.add_stock(
                    Stock(
                        id=str(uuid.uuid4()),
                        name=name,
                        model=target_card.model,
                        price=price,
                        link=link,
                        expired=False,
                        telegram_message_id=message.message_id
                    )
                )

    @staticmethod
    def parse_price(price: str) -> float:
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

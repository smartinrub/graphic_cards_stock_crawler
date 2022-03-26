import json
import logging
import os
import time
import uuid
from typing import List

from graphic_cards_stock_crawler.utils.db import GraphicCard, Stock, DB
from graphic_cards_stock_crawler.utils.retailers import *
from graphic_cards_stock_crawler.utils.telegram_bot import TelegramBot


class RetailerHandler:
    telegram_bot: TelegramBot = TelegramBot()
    db: DB = DB()

    def process_coolmod(self, response):
        logging.info("Start processing Graphic Cards Stock from COOLMOD.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

        graphic_cards_found = response.selector.xpath(
            '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div')
        logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
        for graphic_card in graphic_cards_found:
            if 'Agotado' in graphic_card.xpath('normalize-space(.//span[@class="stock off"])')[0].extract():
                continue

            name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
            if not name:
                continue
            path = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
            price = self.__parse_price(graphic_card.xpath(
                'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"])')[
                                           0].extract())
            self.__process_graphic_card(name, price, f'{coolmod_base_url}{path}', "coolmod", graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "coolmod")

    def process_ldlc(self, response):
        logging.info("Start processing Graphic Cards Stock from LDLC.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

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
            self.__process_graphic_card(name, price, f'{ldlc_base_url}{path}', "ldlc", graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "ldlc")

    def process_vsgamers(self, response):
        logging.info("Start processing Graphic Cards Stock from VS Gamers.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

        graphic_cards_found = response.selector.xpath(
            '//div[@class="vs-product-list"]/div[@class="vs-product-list-item"]')
        logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
        for graphic_card in graphic_cards_found:
            name = graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-title"])')[0].extract()
            if not name:
                continue
            path = graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-title"]/a/@href)')[
                0].extract()
            price = self.__parse_price(
                graphic_card.xpath('normalize-space(.//span[@class="vs-product-card-prices-price"])')[0].extract())
            self.__process_graphic_card(name, price, f'{vsgamers_base_url}{path}', "vsgamers",
                                        graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "vsgamers")

    def process_aussar(self, response):
        logging.info("Start processing Graphic Cards Stock from AUSSAR.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

        graphic_cards_found = response.selector.xpath(
            '//div[@class="product_list grid  product-list-default "]/div[@class="row"]')

        logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
        for graphic_card in graphic_cards_found:
            name = graphic_card.xpath('normalize-space(.//h3)')[0].extract()
            price = self.__parse_price(graphic_card.xpath('normalize-space(.//span[@class="price"])')[0].extract())
            link = graphic_card.xpath('normalize-space(.//h3/a/@href)')[0].extract()
            self.__process_graphic_card(name, price, link, "aussar", graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "aussar")

    def process_ultimainformatica(self, response):
        logging.info("Start processing Graphic Cards Stock from Ultima Informatica.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

        graphic_cards_found = response.selector.xpath('//div[@class="products row products-grid"]/div')

        logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
        for graphic_card in graphic_cards_found:
            if "carrito" not in graphic_card.xpath('normalize-space(.//div[@class="product-add-cart"])')[0].extract():
                continue

            name = graphic_card.xpath('normalize-space(.//h3)')[0].extract()

            # 100 / 107 x 1.21 (IVA) = 1,130841121495327
            tax_rate = 1.130841121495327
            price = round(self.__parse_price(
                graphic_card.xpath('normalize-space(.//span[@class="product-price"])')[0].extract()) * tax_rate, 2)
            link = graphic_card.xpath('normalize-space(.//h3/a/@href)')[0].extract()
            self.__process_graphic_card(name, price, link, "ultimainformatica", graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "ultimainformatica")

    def process_redcomputer(self, response):
        logging.info("Start processing Graphic Cards Stock from RED COMPUTER.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

        graphic_cards_found = response.selector.xpath('//div[@class="products row products-grid"]/div')

        logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
        for graphic_card in graphic_cards_found:
            name = graphic_card.xpath('normalize-space(.//span[@class="h3 product-title"])')[0].extract()
            price = self.__parse_price(
                graphic_card.xpath('normalize-space(.//span[@class="product-price"])')[0].extract())
            link = graphic_card.xpath('normalize-space(.//span/a/@href)')[0].extract()
            self.__process_graphic_card(name, price, link, "redcomputer", graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "redcomputer")

    def process_neobyte(self, response):
        # TODO: Go to the next page
        logging.info("Start processing Graphic Cards Stock from NEOBYTE.")
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        processed_cards = []

        graphic_cards_found = response.selector.xpath(
            '//section[@id="products"]/div/div[@id="js-product-list"]/div/div')

        logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
        for graphic_card in graphic_cards_found:
            if "carrito" not in graphic_card.xpath('normalize-space(.//div[@class="product-add-cart"])')[0].extract():
                continue
            name = graphic_card.xpath('normalize-space(.//span[@class="h3 product-title"])')[0].extract()
            price = self.__parse_price(
                graphic_card.xpath('normalize-space(.//span[@class="product-price"])')[0].extract())
            link = graphic_card.xpath('normalize-space(.//span/a/@href)')[0].extract()
            self.__process_graphic_card(name, price, link, "neobyte", graphic_card_targets)
            processed_cards.append(name)

        self.__expire_cards(processed_cards, "neobyte")

    def __expire_cards(self, processed_cards: list, retailer: str):
        non_expired_stocks: List[Stock] = self.db.get_non_expired_stock_by_retailer(retailer)
        for non_expired_stock in non_expired_stocks:
            if non_expired_stock.name not in processed_cards:
                self.db.set_expired_stock(non_expired_stock.id)
                self.telegram_bot.edit_message(
                    chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                    message_id=non_expired_stock.telegram_message_id,
                    name=non_expired_stock.name,
                    chipset=non_expired_stock.chipset,
                    price=str(non_expired_stock.price),
                    link=non_expired_stock.link
                )
                logging.info(f"Expired [{non_expired_stock.name}].")

    @staticmethod
    def __parse_price(price: str) -> float:
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

    def __process_graphic_card(self, name: str, price: float, link: str, retailer: str,
                               graphic_card_targets: list):
        saved_stock: List[Stock] = self.db.get_all_non_expired_stock_by_name(name)

        if len(saved_stock) != 0:
            logging.info(f"Skipping: [{name}]. Already notified.")
            return

        for target_card in graphic_card_targets:
            if target_card.chipset.lower() in name.lower() \
                    and not self.__is_excluded(name.lower(), target_card.exclusion) \
                    and target_card.max_price >= price:
                message = self.telegram_bot.send_message(os.getenv('TELEGRAM_CHAT_ID'), name, target_card.chipset,
                                                         str(price), link)
                self.db.add_stock(
                    Stock(
                        id=str(uuid.uuid4()),
                        name=name,
                        chipset=target_card.chipset,
                        price=price,
                        link=link,
                        expired=False,
                        telegram_message_id=message.message_id,
                        retailer=retailer
                    )
                )
                logging.info(f"Processed [{name}].")
                time.sleep(1)

    @staticmethod
    def __is_excluded(name: str, exclusion: str) -> bool:
        if exclusion:
            return exclusion.lower() in name
        return False

import json
import logging
import os
import uuid
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler
from typing import List

import scrapy

from graphic_cards_stock_crawler.utils.db import GraphicCard, Stock, DB
from graphic_cards_stock_crawler.utils.telegram_bot import TelegramBot

coolmod_base_url = 'https://www.coolmod.com'
ldlc_base_url = 'https://www.ldlc.com'
vsgamers_base_url = 'https://www.vsgamers.es'
aussar_base_url = 'https://www.aussar.es'
ultimainformatica_base_url = 'https://ultimainformatica.com'
redcomputer_base_url = 'https://tienda.redcomputer.es'
neobyte_base_url = 'https://www.neobyte.es'

PAPERTRAIL_URL = os.getenv('PAPERTRAIL_URL')
PAPERTRAIL_PORT = int(os.getenv('PAPERTRAIL_PORT'))


class GraphicCardsSpider(scrapy.Spider):
    logging: logging
    telegram_bot: TelegramBot = TelegramBot()
    db: DB = DB()

    name = "graphic_cards_stock"
    start_urls = [
        f'{coolmod_base_url}/tarjetas-graficas/',
        # f'{ldlc_base_url}/es-es/informatica/piezas-de-informatica/tarjeta-grafica/c4684/+fdi-1+fv1026-5801.html',
        f'{vsgamers_base_url}/category/componentes/tarjetas-graficas?hidden_without_stock=true&filter-tipo=nvidia-537',
        f'{aussar_base_url}/tarjetas-graficas/tarjetas-graficas-nvidia//Disponibilidad-En%20stock/?q=Disponibilidad-En+stock',
        f'{ultimainformatica_base_url}/34-tarjetas-graficas/s-1/con_stock_en_tienda-stock_central/categorias_2-tarjetas_graficas',
        f'{redcomputer_base_url}/tarjetas-graficas-nvidia-rtx-10000020?productListView=list',
        f'{neobyte_base_url}/tarjetas-graficas-111?q=Tarjeta+gráfica-NVIDIA+RTX+Serie+3000&productListView=list'
    ]

    def __init__(self, **kwargs):
        log_file = './crawler.log'

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        rotating_file_log = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=1)
        rotating_file_log.setLevel(logging.INFO)
        rotating_file_log.setFormatter(formatter)
        root_logger.addHandler(rotating_file_log)

        syslog = SysLogHandler(address=(PAPERTRAIL_URL, PAPERTRAIL_PORT))
        syslog.setFormatter(formatter)
        root_logger.addHandler(syslog)

        super().__init__(**kwargs)

    def parse(self, response, **kwargs):
        graphic_card_targets: List[GraphicCard] = self.db.get_all_graphic_cards()

        if "coolmod" in response.url:
            logging.info("Start processing Graphic Cards Stock from COOLMOD.")

            processed_cards = []

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
                self.process_graphic_card(logging, name, price, f'{coolmod_base_url}{path}', "coolmod",
                                          graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "coolmod")

        elif "ldlc" in response.url:
            logging.info("Start processing Graphic Cards Stock from LDLC.")

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
                self.process_graphic_card(logging, name, price, f'{ldlc_base_url}{path}', "ldlc", graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "ldlc")

        elif "vsgamers" in response.url:
            logging.info("Start processing Graphic Cards Stock from VS Gamers.")

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
                price = self.parse_price(
                    graphic_card.xpath('normalize-space(.//div[@class="vs-product-card-prices"])')[0].extract())
                self.process_graphic_card(logging, name, price, f'{vsgamers_base_url}{path}', "vsgamers",
                                          graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "vsgamers")

        elif "aussar" in response.url:
            logging.info("Start processing Graphic Cards Stock from AUSSAR.")

            processed_cards = []

            graphic_cards_found = response.selector.xpath(
                '//div[@class="product_list grid  product-list-default "]/div[@class="row"]')

            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                name = graphic_card.xpath('normalize-space(.//h3)')[0].extract()
                price = self.parse_price(graphic_card.xpath('normalize-space(.//span[@class="price"])')[0].extract())
                link = graphic_card.xpath('normalize-space(.//h3/a/@href)')[0].extract()
                self.process_graphic_card(logging, name, price, link, "aussar", graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "aussar")

        elif "ultimainformatica" in response.url:
            logging.info("Start processing Graphic Cards Stock from Ultima Informatica.")

            processed_cards = []

            graphic_cards_found = response.selector.xpath('//div[@class="products row products-grid"]/div')

            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                if ("carrito" not in graphic_card.xpath('normalize-space(.//div[@class="product-add-cart"])')[
                    0].extract()):
                    continue

                name = graphic_card.xpath('normalize-space(.//h3)')[0].extract()

                # 100 / 107 x 1.21 (IVA) = 1,130841121495327
                tax_rate = 1.130841121495327
                price = round(self.parse_price(
                    graphic_card.xpath('normalize-space(.//span[@class="product-price"])')[0].extract()) * tax_rate, 2)
                link = graphic_card.xpath('normalize-space(.//h3/a/@href)')[0].extract()
                self.process_graphic_card(logging, name, price, link, "ultimainformatica", graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "ultimainformatica")

        elif "redcomputer" in response.url:
            logging.info("Start processing Graphic Cards Stock from RED COMPUTER.")

            processed_cards = []

            graphic_cards_found = response.selector.xpath('//div[@class="products row products-list"]/div')

            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                name = graphic_card.xpath('normalize-space(.//div[@class="product-description-short"])')[0].extract()
                price = self.parse_price(
                    graphic_card.xpath('normalize-space(.//span[@class="product-price"])')[0].extract())
                link = graphic_card.xpath('normalize-space(.//span/a/@href)')[0].extract()
                self.process_graphic_card(logging, name, price, link, "redcomputer", graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "redcomputer")

        elif "neobyte" in response.url:
            # TODO: Go to the next page
            logging.info("Start processing Graphic Cards Stock from NEOBYTE.")

            processed_cards = []

            graphic_cards_found = response.selector.xpath(
                '//section[@id="products"]/div/div[@id="js-product-list"]/div/div')

            logging.info(f"Found {len(graphic_cards_found.extract())} to process.")
            for graphic_card in graphic_cards_found:
                if ("carrito" not in graphic_card.xpath('normalize-space(.//div[@class="product-add-cart"])')[
                    0].extract()):
                    continue
                name = graphic_card.xpath('normalize-space(.//span[@class="h3 product-title"])')[0].extract()
                price = self.parse_price(
                    graphic_card.xpath('normalize-space(.//span[@class="product-price"])')[0].extract())
                link = graphic_card.xpath('normalize-space(.//span/a/@href)')[0].extract()
                self.process_graphic_card(logging, name, price, link, "neobyte", graphic_card_targets)
                processed_cards.append(name)

            self.expire_cards(logging, processed_cards, "neobyte")

    def expire_cards(self, logging: logging, processed_cards: list, retailer: str):
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
    def parse_price(price: str) -> float:
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

    def process_graphic_card(self, logging: logging, name: str, price: float, link: str, retailer: str,
                             graphic_card_targets: list):
        saved_stock: List[Stock] = self.db.get_all_non_expired_stock_by_name(name)

        if len(saved_stock) != 0:
            logging.info(f"Skipping: [{name}]. Already notified.")
            return

        for target_card in graphic_card_targets:
            if target_card.chipset.lower() in name.lower() \
                    and not self.is_excluded(name.lower(), target_card.exclusion) \
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

    @staticmethod
    def is_excluded(name: str, exclusion: str) -> bool:
        if exclusion:
            return exclusion.lower() in name
        return False

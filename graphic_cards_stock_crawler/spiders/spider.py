import logging
import os
from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler

import scrapy

from graphic_cards_stock_crawler.service.retailer_service import RetailerHandler
from graphic_cards_stock_crawler.utils.retailers import *


class GraphicCardsSpider(scrapy.Spider):
    retailer_handler: RetailerHandler = RetailerHandler()

    name = "graphic_cards_stock"
    start_urls = [
        f'{coolmod_base_url}/tarjetas-graficas/',
        # f'{ldlc_base_url}/es-es/informatica/piezas-de-informatica/tarjeta-grafica/c4684/+fdi-1+fv1026-5801.html',
        f'{vsgamers_base_url}/category/componentes/tarjetas-graficas?hidden_without_stock=true&filter-tipo=nvidia-537',
        f'{aussar_base_url}/tarjetas-graficas/tarjetas-graficas-nvidia//Disponibilidad-En%20stock/?q=Disponibilidad-En+stock',
        # f'{ultimainformatica_base_url}/34-tarjetas-graficas/s-1/con_stock_en_tienda-stock_central/categorias_2-tarjetas_graficas',
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

        syslog = SysLogHandler(address=(os.getenv('PAPERTRAIL_URL'), int(os.getenv('PAPERTRAIL_PORT'))))
        syslog.setLevel(logging.ERROR)
        syslog.setFormatter(formatter)
        root_logger.addHandler(syslog)

        super().__init__(**kwargs)

    def parse(self, response, **kwargs):

        if "coolmod" in response.url:
            self.retailer_handler.process_coolmod(response)
        elif "ldlc" in response.url:
            self.retailer_handler.process_ldlc(response)
        elif "vsgamers" in response.url:
            self.retailer_handler.process_vsgamers(response)
        elif "aussar" in response.url:
            self.retailer_handler.process_aussar(response)
        elif "ultimainformatica" in response.url:
            self.retailer_handler.process_ultimainformatica(response)
        elif "redcomputer" in response.url:
            self.retailer_handler.process_redcomputer(response)
        elif "neobyte" in response.url:
            self.retailer_handler.process_neobyte(response)

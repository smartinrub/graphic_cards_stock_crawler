import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from graphic_cards_stock_crawler.spiders import spider
from graphic_cards_stock_crawler.utils.db import DB, Stock, GraphicCard
from .responses.websites_example import fake_response_from_file


class GraphicCardsStockSpiderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['TELEGRAM_TOKEN'] = "123:ABC"
        cls.spider = spider.GraphicCardsSpider()

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3070',
            max_price=1200
        ),
        GraphicCard(
            chipset='3090',
            max_price=3000
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    def test_parse_coolmod(self, add_stock_mock, send_message):
        # WHEN
        self.spider.parse(fake_response_from_file(
            file_name='coolmod_example.html',
            url='https://www.coolmod.com/tarjetas-graficas/'
        ))

        # THEN
        self.assertEqual(4, add_stock_mock.call_count)
        self.assertEqual(4, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[
        Stock(
            id='c986d542-5d9c-414f-bdc7-8f69be9c802f',
            name='Asus ROG Strix GeForce RTX 3070 OC LHR V2 GAMING 8GB GDDR6 - Tarjeta Gráfica',
            chipset='3070', price=1199.94,
            in_stock_date=datetime.strptime('2021-11-19 16:17:59', '%Y-%m-%d %H:%M:%S'),
            link="https://example.com",
            expired=True
        )
    ]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3070',
            max_price=1200
        ),
        GraphicCard(
            chipset='3090',
            max_price=3000
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    def test_should_skip_when_found_not_expired(self, add_stock_mock, send_message):
        # WHEN
        self.spider.parse(fake_response_from_file(
            file_name='coolmod_example.html',
            url='https://www.coolmod.com/tarjetas-graficas/'
        ))

        # THEN
        self.assertEqual(0, add_stock_mock.call_count)
        self.assertEqual(0, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3080 Ti',
            max_price=2400
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    def test_parse_ldlc(self, add_stock_mock, send_message):
        # WHEN
        self.spider.parse(fake_response_from_file(
            file_name='ldlc_example.html',
            url='https://www.ldlc.com/es-es/informatica/piezas-de-informatica/tarjeta-grafica/c4684/+fdi-1+fv1026-5801.html'
        ))

        # THEN
        self.assertEqual(7, add_stock_mock.call_count)
        self.assertEqual(7, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='T1000',
            max_price=508.2
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    def test_parse_vsgamers(self, add_stock_mock, send_message):
        # WHEN
        self.spider.parse(fake_response_from_file(
            file_name='vsgamers_example.html',
            url='https://www.vsgamers.es/category/componentes/tarjetas-graficas?filter-tipo=nvidia-537&hidden_without_stock=true'
        ))

        # THEN
        self.assertEqual(1, add_stock_mock.call_count)
        self.assertEqual(1, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3060',
            max_price=769
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    def test_parse_aussar(self, add_stock_mock, send_message):
        # WHEN
        self.spider.parse(fake_response_from_file(
            file_name='aussar_example.html',
            url='https://www.aussar.es/tarjetas-graficas/tarjetas-graficas-nvidia//Disponibilidad-En%20stock/?q=Disponibilidad-En+stock'
        ))

        # THEN
        self.assertEqual(1, add_stock_mock.call_count)
        self.assertEqual(1, send_message.call_count)
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import telegram
from telegram import Bot

from graphic_cards_stock_crawler.spiders import spider
from graphic_cards_stock_crawler.utils.db import DB, Stock, GraphicCard
from .responses.coolmod_example import fake_response_from_file


class GraphicCardsStockSpiderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['TELEGRAM_TOKEN'] = "123:ABC"
        cls.spider = spider.GraphicCardsSpider()

    @patch.object(DB, 'get_all_stock_by_name', MagicMock(return_value=[
        Stock(id='c986d542-5d9c-414f-bdc7-8f69be9c802f',
              name='Asus ROG Strix GeForce RTX 3070 OC LHR V2 GAMING 8GB GDDR6 - Tarjeta Gráfica',
              model='3070', price=1199.94,
              in_stock_date=datetime.strptime('2021-11-19 16:17:59', '%Y-%m-%d %H:%M:%S')
              )
    ]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            model='3070',
            max_price=1200
        ),
        GraphicCard(
            model='3090',
            max_price=3000
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch.object(telegram, 'Bot', MagicMock())
    @patch.object(Bot, 'send_message', MagicMock())
    def test_parse(self, add_stock_mock):
        # WHEN
        self.spider.parse(fake_response_from_file('coolmod_example.html'))

        # THEN
        self.assertEqual(4, add_stock_mock.call_count)

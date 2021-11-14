import os
import unittest
# import telegram
from telegram import Bot
import telegram
from unittest.mock import MagicMock, patch

from graphic_cards_stock_crawler.spiders import spider
from .responses.coolmod_example import fake_response_from_file


class GraphicCardsStockSpiderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['MARIADB_USER'] = "root"
        os.environ['MARIADB_PASSWORD'] = "root"
        os.environ['MARIADB_HOST'] = "localhost"
        os.environ['MARIADB_SCHEMA'] = "graphic_cards_stock_crawler"
        os.environ['TELEGRAM_TOKEN'] = "123:ABC"
        cls.spider = spider.GraphicCardsSpider()

    @patch.object(telegram, 'Bot', MagicMock())
    @patch.object(Bot, 'send_message', MagicMock())
    def test_parse(self):
        # WHEN
        results = self.spider.parse(fake_response_from_file('coolmod_example.html'))


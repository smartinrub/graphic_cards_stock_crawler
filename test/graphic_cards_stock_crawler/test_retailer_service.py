import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from graphic_cards_stock_crawler.service import retailer_service
from graphic_cards_stock_crawler.utils.db import DB, Stock, GraphicCard
from .responses.websites_example import fake_response_from_file


class RetailerServiceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['TELEGRAM_TOKEN'] = "123:ABC"
        cls.retailer_service = retailer_service.RetailerHandler()

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3070',
            max_price=1200,
            exclusion='3070 Ti'
        ),
        GraphicCard(
            chipset='3090',
            max_price=3000
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_coolmod(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_coolmod(fake_response_from_file(
            file_name='coolmod_example.html',
            url='https://www.coolmod.com/tarjetas-graficas/'
        ))

        # THEN
        self.assertEqual(3, add_stock_mock.call_count)
        self.assertEqual(3, send_message.call_count)

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
            max_price=1200,
            exclusion='3070 Ti'
        ),
        GraphicCard(
            chipset='3090',
            max_price=3000
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_should_skip_when_found_not_expired(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_coolmod(fake_response_from_file(
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
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_ldlc(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_ldlc(fake_response_from_file(
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
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_vsgamers(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_vsgamers(fake_response_from_file(
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
            max_price=769,
            exclusion='3060 Ti'
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_aussar(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_aussar(fake_response_from_file(
            file_name='aussar_example.html',
            url='https://www.aussar.es/tarjetas-graficas/tarjetas-graficas-nvidia//Disponibilidad-En%20stock/?q=Disponibilidad-En+stock'
        ))

        # THEN
        self.assertEqual(2, add_stock_mock.call_count)
        self.assertEqual(2, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3060',
            max_price=734,
            exclusion='3060 Ti'
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_ultimainformatica(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_ultimainformatica(fake_response_from_file(
            file_name='ultimainformatica_example.html',
            url='https://ultimainformatica.com/34-tarjetas-graficas/s-1/con_stock_en_tienda-stock_central/categorias_2-tarjetas_graficas'
        ))

        # THEN
        self.assertEqual(1, add_stock_mock.call_count)
        self.assertEqual(1, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3070 ti',
            max_price=1049.99
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_redcomputer(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_redcomputer(fake_response_from_file(
            file_name='redcomputer_example.html',
            url='https://tienda.redcomputer.es/tarjetas-graficas-nvidia-rtx-10000020?productListView=list'
        ))

        # THEN
        self.assertEqual(2, add_stock_mock.call_count)
        self.assertEqual(2, send_message.call_count)

    @patch.object(DB, 'get_all_non_expired_stock_by_name', MagicMock(return_value=[]))
    @patch.object(DB, 'get_all_graphic_cards', MagicMock(return_value=[
        GraphicCard(
            chipset='3080 ti',
            max_price=1888.99
        )
    ]))
    @patch('graphic_cards_stock_crawler.utils.db.DB.add_stock')
    @patch('graphic_cards_stock_crawler.utils.telegram_bot.Bot.send_message')
    @patch.object(DB, 'get_non_expired_stock_by_retailer', MagicMock(return_value=[]))
    def test_parse_neobyte(self, add_stock_mock, send_message):
        # WHEN
        self.retailer_service.process_neobyte(fake_response_from_file(
            file_name='neobyte_example.html',
            url='https://www.neobyte.es/tarjetas-graficas-111?q=Tarjeta+gr%C3%A1fica-NVIDIA+RTX+Serie+3000&productListView=list'
        ))

        # THEN
        self.assertEqual(1, add_stock_mock.call_count)
        self.assertEqual(1, send_message.call_count)

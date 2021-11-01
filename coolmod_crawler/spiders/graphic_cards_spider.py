import os
import scrapy
import telegram

target_cards: list = [
    {
        "name": "3060",
        "max_price": 450,
        "exclusions": ["3060 Ti"]
    },
    {
        "name": "3060 Ti",
        "max_price": 650,
        "exclusions": []
    },
    {
        "name": "3070",
        "max_price": 700,
        "exclusions": ["3070 Ti"]
    },
    {
        "name": "3070 Ti",
        "max_price": 900,
        "exclusions": []
    },
    {
        "name": "3080",
        "max_price": 1000,
        "exclusions": ["3080 Ti"]
    },
    {
        "name": "3080 Ti",
        "max_price": 1200,
        "exclusions": []
    },
    {
        "name": "3090",
        "max_price": 2800,
        "exclusions": ["3090 Ti"]
    },
]

telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = "1652193495"


class GraphicCardsSpider(scrapy.Spider):
    name = "graphic_cards"
    start_urls = [
        'https://www.coolmod.com/tarjetas-graficas/appliedfilters/9678__9675__9728__8557__9674__9727',
    ]

    def parse(self, response, **kwargs):
        bot = telegram.Bot(token=telegram_token)
        result = []
        for graphic_card in response.selector.xpath(
                '//div[@class="row categorylistproducts listtype-a hiddenproducts display-none"]/div'):
            name = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/text())')[0].extract()
            link = graphic_card.xpath('normalize-space(.//div[@class="productName"]//a/@href)')[0].extract()
            price = graphic_card.xpath(
                'normalize-space(.//div[@class="productPrice position-relative"]//div[@class="discount"]//span[@class="totalprice"]/text())')[
                0].extract()

            for target_card in target_cards:
                if target_card['name'] in name and target_card['max_price'] >= self.parse_price(price):
                    # TODO: follow link to check if it's really available
                    if name not in result:
                        result.append(name)
                        message = {
                            'name': name,
                            'link': f'https://www.coolmod.com{link}'
                        }
                        bot.send_message(text=message, chat_id=telegram_chat_id)

    def parse_price(self, price: str):
        return float(price
                     .replace("€", "")
                     .replace(".", "")
                     .replace(",", ".")
                     .strip()
                     )

import os

import telegram
from telegram import Bot
from telegram.parsemode import ParseMode
from telegram.utils.helpers import escape_markdown


class TelegramBot:
    bot: Bot = None

    def __get_bot(self) -> Bot:
        if not self.bot:
            self.bot = telegram.Bot(token=os.getenv('TELEGRAM_TOKEN'))
        return self.bot

    def send_message(self, chat_id: str, name: str, model: str, price: str, link: str):
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
        self.__get_bot().send_message(text=message, chat_id=chat_id, parse_mode=ParseMode.MARKDOWN_V2)

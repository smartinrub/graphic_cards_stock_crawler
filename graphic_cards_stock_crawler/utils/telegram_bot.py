import os

import telegram
from telegram import Bot


class TelegramBot:
    bot: Bot = None

    def get_bot(self) -> Bot:
        if not self.bot:
            self.bot = telegram.Bot(token=os.getenv('TELEGRAM_TOKEN'))
        return self.bot

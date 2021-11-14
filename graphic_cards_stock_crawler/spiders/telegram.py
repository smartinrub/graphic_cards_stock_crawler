import os

import telegram

__bot = None


def get_bot():
    global __bot
    if not __bot:
        __bot = telegram.Bot(token=os.getenv('TELEGRAM_TOKEN'))
    return __bot

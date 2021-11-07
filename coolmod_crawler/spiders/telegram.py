import os

import telegram

telegram_token = os.getenv('TELEGRAM_TOKEN')

__bot = None


def get_bot():
    global __bot
    if not __bot:
        __bot = telegram.Bot(token=telegram_token)
    return __bot

import logging

from settings.models import Setting
from telegram.ext import Updater

logger = logging.getLogger()


def get_telegram_token() -> str:
    telegram_token = Setting.objects.first().telegram_bot_token
    return telegram_token.value


def get_telegram_bot_name() -> str:
    try:
        updater = Updater(token=get_telegram_token())                                 # Telegram client
        return updater.bot.username
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot name request')
        return 'RekonoBot'

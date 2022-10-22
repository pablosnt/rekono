import logging
from typing import Optional

from system.models import System
from telegram.ext import Updater

logger = logging.getLogger()


def get_telegram_token() -> str:
    return System.objects.first().telegram_bot_token


def get_telegram_bot_name() -> Optional[str]:
    try:
        updater = Updater(token=get_telegram_token())                                 # Telegram client
        return updater.bot.username
    except Exception:
        logger.error('[Telegram Bot] Error during Telegram bot name request')
        return None

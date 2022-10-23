import logging

from system.models import System
from telegram import ParseMode
from telegram.ext import Updater

logger = logging.getLogger()                                                    # Rekono logger


def send_message(chat_id: int, text: str) -> None:
    '''Send Telegram message.

    Args:
        chat_id (int): Destinatary Telegram chat Id
        text (str): Text message with markdown style
    '''
    try:
        updater = Updater(token=System.objects.first().telegram_bot_token)                           # Telegram client
        updater.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)      # Send Telegram text message
    except Exception as ex:
        logger.error(f'[Telegram] Error during Telegram message sending: {str(ex)}')

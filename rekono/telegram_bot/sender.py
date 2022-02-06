from telegram import ParseMode
from telegram.ext import Updater

from rekono.settings import TELEGRAM_TOKEN


def send_message(chat_id: int, text: str) -> None:
    '''Send Telegram message.

    Args:
        chat_id (int): Destinatary Telegram chat Id
        text (str): Text message with markdown style
    '''
    updater = Updater(token=TELEGRAM_TOKEN)                                     # Telegram client
    updater.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)  # Send Telegram text message

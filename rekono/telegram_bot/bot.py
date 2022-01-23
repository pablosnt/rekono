from telegram import ParseMode
from telegram.ext import CommandHandler, Updater
from telegram_bot.commands import help, logout, start

from rekono.settings import TELEGRAM_TOKEN


def send_message(chat_id: int, text: str) -> None:
    '''Send Telegram message.

    Args:
        chat_id (int): Destinatary Telegram chat Id
        text (str): Text message with Markdown style
    '''
    updater = Updater(token=TELEGRAM_TOKEN)                                     # Telegram client
    updater.bot.send_message(chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)  # Send Telegram text message


def deploy() -> None:
    '''Start listenning for commands.'''
    updater = Updater(token=TELEGRAM_TOKEN)                                     # Telegram client
    updater.dispatcher.add_handler(CommandHandler('start', start))              # Start command
    updater.dispatcher.add_handler(CommandHandler('logout', logout))            # Logout command
    updater.dispatcher.add_handler(CommandHandler('help', help))                # Help command
    updater.start_polling()                                                     # Start Telegram Bot

from telegram import ParseMode
from telegram.ext import CommandHandler, Updater
from telegram_bot.commands import help, logout, start
from telegram_bot.utils import build_execution_notification_message

from rekono.settings import REKONO_ADDRESS, TELEGRAM_TOKEN


def send_html_message(chat_id: int, parameters: dict) -> None:
    parameters['rekono_address'] = REKONO_ADDRESS
    updater = Updater(token=TELEGRAM_TOKEN)
    text = build_execution_notification_message(parameters)
    updater.bot.send_message(chat_id, text=text, parse_mode=ParseMode.HTML)


def execute():
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('logout', logout))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.start_polling()

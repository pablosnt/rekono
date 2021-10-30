from typing import Any

from telegram.ext import CommandHandler, Updater
from telegram_bot.commands import help, logout, start

from rekono.settings import TELEGRAM_TOKEN


def send_notification(execution: Any, findings: list) -> None:
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.bot.send_message(execution.task.executor.telegram_id, text='Finding notification!')


def execute():
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('logout', logout))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.start_polling()

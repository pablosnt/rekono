from typing import Any

from django.core.management.base import BaseCommand
from telegram_bot import bot


class Command(BaseCommand):
    '''Rekono command to deploy Telegram Bot.'''

    help = 'Deploy Telegram Bot'

    def handle(self, *args: Any, **options: Any) -> None:
        '''Deploy Telegram Bot.'''
        bot.initialize()
        bot.deploy()

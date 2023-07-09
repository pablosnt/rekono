from typing import Any

from django.core.management.base import BaseCommand

from telegram_bot import bot, token


class Command(BaseCommand):
    '''Rekono command to deploy Telegram Bot.'''

    help = 'Deploy Telegram Bot'

    def handle(self, *args: Any, **options: Any) -> None:
        '''Deploy Telegram Bot.'''
        token.wait_until_telegram_token_is_configured(60)                       # Wait until token is configured
        bot.initialize()                                                        # Initialize Telegram Bot
        bot.deploy()                                                            # Deploy Telegram Bot

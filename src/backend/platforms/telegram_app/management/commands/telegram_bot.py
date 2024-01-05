from typing import Any

from django.core.management.base import BaseCommand

from platforms.telegram_app.bot.bot import TelegramBot


class Command(BaseCommand):
    help = "Deploy Telegram Bot"
    bot = TelegramBot()

    def handle(self, *args: Any, **options: Any) -> None:
        self.bot.deploy()

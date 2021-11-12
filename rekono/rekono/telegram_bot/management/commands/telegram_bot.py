from typing import Any, Optional

from django.core.management.base import BaseCommand
from telegram_bot.bot import execute


class Command(BaseCommand):
    help = 'Starts Telegram Bot'

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        execute()

"""Django management command for deploying the Telegram Bot.

Provides a management command to start and deploy the Telegram Bot
service through Django's command-line interface.
"""

import warnings
from typing import Any

from django.core.management.base import BaseCommand

warnings.filterwarnings("ignore", category=SyntaxWarning, module=r".*telegram_app.*")

# Imported after the filter above so the SyntaxWarning it raises on import is already suppressed
from platforms.telegram_app.bot import TelegramBot  # noqa: E402


class Command(BaseCommand):
    """Management command to deploy and start the Telegram Bot.

    Initializes and starts the Telegram Bot polling process for handling
    user interactions and security testing commands.

    Attributes:
        help (str): Command help text displayed in management interface.
        bot (TelegramBot): The Telegram Bot instance to deploy.
    """

    help = "Deploy Telegram Bot"
    bot = TelegramBot()

    def handle(self, *args: Any, **options: Any) -> None:
        """Deploy the Telegram Bot and keep it polling until interrupted.

        Blocks on TelegramBot.deploy() for as long as the polling loop runs. A
        KeyboardInterrupt (e.g. Ctrl+C) stops the loop and is caught here so the
        shutdown is logged instead of raising a traceback.

        Args:
            *args (Any): Positional arguments passed to the command.
            **options (Any): Keyword arguments passed to the command.
        """
        try:
            self.bot.logger.info("Deploying telegram bot")
            self.bot.deploy()
        except KeyboardInterrupt:
            self.bot.logger.info("Telegram bot is down")

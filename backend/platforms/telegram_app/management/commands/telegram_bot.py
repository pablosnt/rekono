"""Command that runs the Telegram bot.

The bot runs as its own process, since it has to keep asking Telegram for the
messages that the users write.
"""

from typing import Any

from django.core.management.base import BaseCommand

from platforms.telegram_app.bot import TelegramBot


class Command(BaseCommand):
    """Command that runs the Telegram bot until it's stopped.

    Attributes:
        help: Description of the command shown by the Django help.
        bot: Bot that attends the messages of the users.
    """

    help = "Deploy Telegram Bot"
    bot = TelegramBot()

    def handle(self, *args: Any, **options: Any) -> None:
        """Run the bot, logging when it's stopped instead of failing.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        try:
            self.bot.logger.info("Deploying telegram bot")
            self.bot.deploy()
        except KeyboardInterrupt:
            self.bot.logger.info("Telegram bot is down")

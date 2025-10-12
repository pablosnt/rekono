"""Telegram Bot command handling and conversation management.

Provides bot command framework, conversation workflows, and interactive
interfaces for Rekono security testing operations through Telegram.
"""

import asyncio
import time
from warnings import filterwarnings

from telegram.error import Forbidden, InvalidToken
from telegram.ext import Application
from telegram.warnings import PTBUserWarning

from platforms.telegram_app.bot.commands import ClearProject, Help, Logout, ShowProject, Start
from platforms.telegram_app.bot.conversations import Cancel, NewPort, NewTarget, Process, SelectProject, Tool
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramSettings

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


# TODO: Telegram bot is not working at all.
class TelegramBot(BaseTelegram):
    """Main Telegram Bot class for handling security testing commands and conversations.

    Manages the complete lifecycle of the Telegram Bot including command registration,
    handler setup, and polling operations. Integrates all available commands and
    conversation workflows for interactive security testing operations.

    Attributes:
        commands (list): List of available bot command handlers including commands
                        and conversation workflows for security testing operations.
    """

    commands = [
        Start(),
        Logout(),
        ShowProject(),
        ClearProject(),
        SelectProject(),
        NewTarget(),
        NewPort(),
        Tool(),
        Process(),
    ]

    def __init__(self) -> None:
        """Initialize the Telegram Bot with all available commands and help system.

        Adds the Help command with references to all other commands and initializes
        the base Telegram application framework.
        """
        self.commands.append(Help(self.commands + [Cancel()]))
        super().__init__()

    async def post_init(self, application: Application) -> None:
        """Initialize bot commands and register handlers after application startup.

        Registers all command handlers with the Telegram application and sets up
        the bot command menu for user interaction.

        Args:
            application (Application): The Telegram Bot application instance.
        """
        bot_commands = []
        for command in self.commands:
            bot_commands.append((command.command_name, command.help))
            application.add_handler(command)
        await application.bot.set_my_commands(bot_commands)

    def _wait_for_token(self, sleep_time: int = 60) -> None:
        """Wait for valid Telegram Bot token configuration before starting.

        Continuously checks for a valid Telegram Bot token in settings and waits
        if not configured. Handles token validation and application initialization.

        Args:
            sleep_time (int): Time in seconds to wait between token checks.
                             Defaults to 60 seconds.
        """
        self.settings = TelegramSettings.objects.first()
        if not self.settings or not self.settings.secret:
            del self.app  # Remove cached_property value, so it will be regenerated
            self.logger.info("[Telegram Bot] Waiting while Telegram token is not configured")
        while not self.settings or not self.settings.secret:
            time.sleep(sleep_time)
            self.settings = TelegramSettings.objects.first()
        if not self.app or not self.app.updater or not self.app.bot:
            if self.settings.secret:
                self.handle_invalid_token(False)
            self._wait_for_token(sleep_time)
        # TODO: Remove if not needed
        # else:
        #     self.initialize()

    def deploy(self) -> None:
        """Deploy and start the Telegram Bot with polling mode.

        Starts the bot polling process after ensuring valid token configuration.
        Handles token validation errors and restarts the deployment process if needed.
        """
        self._wait_for_token()
        if not self.app or not self.app.updater or not self.app.bot:
            return self.deploy()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                asyncio.set_event_loop(asyncio.new_event_loop())
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        try:
            self.app.run_polling()
        except (InvalidToken, Forbidden):
            self.handle_invalid_token()
            return self.deploy()

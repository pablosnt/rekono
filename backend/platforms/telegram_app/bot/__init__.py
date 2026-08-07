"""Telegram bot that lets the users work with Rekono from a chat.

A command is either a single answer or a conversation that asks whatever it needs
one question at a time, so the users never have to write anything that can be
chosen from a list.
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


class TelegramBot(BaseTelegram):
    """Bot that attends the commands that the users write in their chats.

    Attributes:
        commands: Commands that the bot answers to.
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
        """Prepare the bot, building its help message from its own commands."""
        # Cancel isn't a command of the bot, it's a fallback of every conversation, but the
        # users need to know that it exists
        self.commands.append(Help(self.commands + [Cancel()]))
        super().__init__()

    async def post_init(self, application: Application) -> None:
        """Register the commands in the bot and in the Telegram command menu.

        Args:
            application: Bot client that was created.
        """
        bot_commands = []
        for command in self.commands:
            bot_commands.append((command.command_name, command.help))
            application.add_handler(command)
        await application.bot.set_my_commands(bot_commands)

    def _wait_for_token(self, sleep_time: int = 60) -> None:
        """Wait until a bot token that Telegram accepts is configured.

        Args:
            sleep_time: Seconds to wait between two checks of the configuration.
        """
        self.settings = TelegramSettings.objects.first()
        if not self.settings or not self.settings.secret:
            self._app = None
            self._initialized = False
            self.logger.info("[Telegram Bot] Waiting while Telegram token is not configured")
        while not self.settings or not self.settings.secret:
            time.sleep(sleep_time)
            self.settings = TelegramSettings.objects.first()
        # The client can't be created if Telegram rejects the token, so it's removed and the
        # users are given the chance to configure another one
        if not self.app or not self.app.updater or not self.app.bot:
            if self.settings.secret:
                self.handle_invalid_token(False)
            self._wait_for_token(sleep_time)

    def deploy(self) -> None:
        """Run the bot, asking Telegram for the messages that the users write.

        The bot waits until a valid token is configured instead of failing, and it
        starts again if Telegram rejects the token while it's running.
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

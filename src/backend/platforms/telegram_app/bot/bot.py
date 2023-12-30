import asyncio
import logging
import time
from warnings import filterwarnings

from platforms.telegram_app.bot.commands import (
    ClearProject,
    Help,
    Logout,
    ShowProject,
    Start,
)
from platforms.telegram_app.bot.conversations import (
    Cancel,
    NewPort,
    NewTarget,
    NewTechnology,
    NewVulnerability,
    Process,
    SelectProject,
    Tool,
)
from typing import cast
from telegram.ext import Application
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramSettings
from telegram.error import Forbidden, InvalidToken
from telegram.ext import Application
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

logger = logging.getLogger()


class TelegramBot(BaseTelegram):
    commands = [
        Start(),
        Logout(),
        ShowProject(),
        ClearProject(),
        SelectProject(),
        NewTarget(),
        NewPort(),
        NewTechnology(),
        NewVulnerability(),
        Tool(),
        Process(),
    ]

    def __init__(self) -> None:
        self.commands.append(Help(self.commands + [Cancel()]))
        super().__init__()

    async def _post_init(self, application: Application) -> None:
        bot_commands = []
        for command in self.commands:
            bot_commands.append((command.get_name(), command.help))
            application.add_handler(command)
        await application.bot.set_my_commands(bot_commands)

    def _wait_for_token(self, sleep_time: int = 60) -> None:
        self.settings = TelegramSettings.objects.first()
        first_iteration = True
        while not self.settings or not self.settings.secret:
            if first_iteration:
                logger.info(
                    "[Telegram Bot] Waiting while Telegram token is not configured"
                )
                first_iteration = False
            time.sleep(sleep_time)
            self.settings = TelegramSettings.objects.first()
        self.app = self._get_app()
        if not self.app or not self.app.updater or not self.app.bot:
            if self.settings.secret:
                self._handle_invalid_token(False)
            self._wait_for_token(sleep_time)

    def deploy(self) -> None:
        self._wait_for_token()
        if not self.app or not self.app.updater or not self.app.bot:
            return self.deploy()
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.app.run_polling()
        except (InvalidToken, Forbidden):
            self._handle_invalid_token()
            return self.deploy()

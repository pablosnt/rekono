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
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramSettings
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

    def _wait_for_token(self, sleep_time: int = 60) -> None:
        if not self.settings or not self.settings.secret:
            logger.info("[Telegram Bot] Waiting while Telegram token is not configured")
        while not self.settings or not self.settings.secret:
            time.sleep(sleep_time)
            self.settings = TelegramSettings.objects.first()
        self.app = self.initialize()
        if not self.app or not self.app.updater or not self.app.bot:
            self.settings.secret = None
            self.settings.save(update_fields=["_token"])
            self._wait_for_token(sleep_time)

    def deploy(self) -> None:
        self._wait_for_token()
        if not self.app or not self.app.updater or not self.app.bot:
            return self.deploy()
        bot_commands = []
        for command in self.commands:
            bot_commands.append((command.get_name(), command.help))
            self.app.add_handler(command)
        asyncio.get_event_loop().run_until_complete(
            self.app.bot.set_my_commands(bot_commands)
        )
        self.app.run_polling()

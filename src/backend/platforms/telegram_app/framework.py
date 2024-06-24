import asyncio
import logging
import threading
import time
from typing import Any, Optional

from platforms.telegram_app.models import TelegramChat, TelegramSettings
from telegram.constants import ParseMode
from telegram.error import Forbidden, InvalidToken, NetworkError
from telegram.ext import Application, CallbackContext
from telegram.helpers import escape_markdown

logger = logging.getLogger()


class BaseTelegram:
    def __init__(self) -> None:
        self.settings = TelegramSettings.objects.first()
        self.app = self.initialize()
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def initialize(self) -> Optional[Application]:
        self.app = self._get_app()
        if self.app and self.app.bot:
            try:
                asyncio.run(self.app.bot.initialize())
            except (InvalidToken, Forbidden):
                self._handle_invalid_token()
        return self.app

    def get_bot_name(self) -> str:
        return self.app.bot.username if self.app and self.app.bot else None

    def _get_app(self) -> Optional[Application]:
        if self.settings and self.settings.secret:
            try:
                return (
                    Application.builder()
                    .token(self.settings.secret)
                    .post_init(self._post_init)
                    .build()
                )
            except (InvalidToken, Forbidden):
                self._handle_invalid_token()
        return None

    async def _post_init(self, application: Application) -> None:
        pass

    def _send_message(
        self, chat: TelegramChat, message: str, reply_markup: Any = None
    ) -> None:
        if self.app and self.app.bot:
            try:
                asyncio.run(
                    self.app.bot.send_message(
                        chat.chat_id,
                        message,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=reply_markup,
                    )
                )
            except NetworkError:
                pass

    def _escape(self, value: str) -> str:
        return escape_markdown(value, version=2)

    def _handle_invalid_token(self, log_error: bool = True) -> None:
        self.settings.secret = None
        self.settings.save(update_fields=["_token"])
        self.app = None
        if log_error:
            logger.error("[Telegram] Authentication error")

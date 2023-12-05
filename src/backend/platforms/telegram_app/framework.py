import asyncio
import logging
from typing import Any

from platforms.telegram_app.models import TelegramChat, TelegramSettings
from telegram.constants import ParseMode
from telegram.error import Forbidden, InvalidToken
from telegram.ext import ApplicationBuilder
from telegram.helpers import escape_markdown

logger = logging.getLogger()


class BaseTelegram:
    def __init__(self, **kwargs: Any) -> None:
        self.settings = TelegramSettings.objects.first()
        self.app = self.initialize()
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def initialize(self) -> None:
        self.app = self._get_app()
        if self.app and self.app.bot:
            try:
                asyncio.run(self.app.bot.initialize())
            except (InvalidToken, Forbidden):
                self._handle_invalid_token()
        return self.app

    def get_bot_name(self) -> str:
        return self.app.bot.username if self.app and self.app.bot else None

    def _get_app(self) -> Any:
        if self.settings and self.settings.secret:
            try:
                return ApplicationBuilder().token(self.settings.secret).build()
            except (InvalidToken, Forbidden):
                self._handle_invalid_token()
            except Exception:
                logger.error("[Telegram] Error creating updater")

    def _send_message(
        self, chat: TelegramChat, message: str, reply_markup: Any = None
    ) -> None:
        if self.app and self.app.bot:
            asyncio.run(
                self.app.bot.send_message(
                    chat.chat_id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            )

    def _escape(self, value: str) -> str:
        return escape_markdown(value, version=2)

    def _handle_invalid_token(self) -> None:
        logger.error("[Telegram] Authentication error")
        self.settings.secret = None
        self.settings.save(update_fields=["_token"])
        self.app = None

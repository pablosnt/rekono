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
        self.app = self._get_app()
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def initialize(self) -> None:
        asyncio.run(self.app.bot.initialize())

    def get_bot_name(self) -> str:
        return self.app.bot.username if self.app and self.app.bot else None

    def _get_app(self) -> Any:
        if self.settings and self.settings.token:
            try:
                return ApplicationBuilder().token(self.settings.token).build()
            except (InvalidToken, Forbidden):
                logger.error("[Telegram] Authentication error")
                self.settings.token = None
                self.settings.save(update_fields=["token"])
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

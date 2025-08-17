import asyncio
from functools import cached_property
from typing import Any

from telegram.constants import ParseMode
from telegram.error import Forbidden, InvalidToken, NetworkError
from telegram.ext import Application
from telegram.helpers import escape_markdown

from framework.logging import LoggingEntity
from platforms.telegram_app.models import TelegramChat, TelegramSettings


class BaseTelegram(LoggingEntity):
    settings = TelegramSettings.objects.first()
    date_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        self.initialize()

    def initialize(self) -> Application | None:
        if self.app and self.app.bot:
            try:
                asyncio.run(self.app.bot.initialize())
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()

    @cached_property
    def app(self) -> Application | None:
        if self.settings and self.settings.secret:
            try:
                return Application.builder().token(self.settings.secret).post_init(self.post_init).build()
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()
        return None

    @cached_property
    def bot_name(self) -> str | None:
        return self.app.bot.username if self.app and self.app.bot else None

    async def post_init(self, application: Application) -> None:
        pass

    def send_message(self, chat: TelegramChat, message: str, reply_markup: Any = None) -> None:
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

    def escape(self, value: str) -> str:
        return escape_markdown(value, version=2)

    def handle_invalid_token(self, log_error: bool = True) -> None:
        self.settings.secret = None
        self.settings.save(update_fields=["_token"])
        del self.app  # Remove cached_property value, so it will be regenerated
        if log_error:
            self.logger.error("[Telegram] Authentication error")

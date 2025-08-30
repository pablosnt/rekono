"""Base framework for Telegram Bot integration with Rekono.

Provides the foundational classes and utilities for Telegram Bot operations
including application management, message handling, and token validation.
"""

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
    """Base class for Telegram Bot integration with application management.

    Provides core functionality for Telegram Bot operations including application
    initialization, message sending, token validation, and error handling.

    Attributes:
        settings (TelegramSettings): Global Telegram Bot settings instance.
        date_format (str): Standard date format for message timestamps.
    """

    settings = TelegramSettings.objects.first()
    date_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        """Initialize the Telegram Bot base class.

        Sets up the bot application and performs initial configuration.
        """
        self.initialize()

    def initialize(self) -> Application | None:
        """Initialize the Telegram Bot application.

        Initializes the bot application if available and handles authentication errors.

        Returns:
            Application | None: The initialized application or None if failed.
        """
        if self.app and self.app.bot:
            try:
                asyncio.run(self.app.bot.initialize())
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()

    @cached_property
    def app(self) -> Application | None:
        """Get the Telegram Bot application instance.

        Creates and configures the Telegram Bot application using the stored token.

        Returns:
            Application | None: The configured bot application or None if no token.
        """
        if self.settings and self.settings.secret:
            try:
                return Application.builder().token(self.settings.secret).post_init(self.post_init).build()
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()
        return None

    @cached_property
    def bot_name(self) -> str | None:
        """Get the Telegram Bot username.

        Returns:
            str | None: The bot username if available, None otherwise.
        """
        return self.app.bot.username if self.app and self.app.bot else None

    async def post_init(self, application: Application) -> None:
        """Post-initialization hook for the Telegram application.

        Override this method to add custom initialization logic after
        the application is created but before it starts.

        Args:
            application (Application): The Telegram Bot application instance.
        """
        pass

    def send_message(self, chat: TelegramChat, message: str, reply_markup: Any = None) -> None:
        """Send a message to a Telegram chat.

        Sends a formatted message to the specified Telegram chat using Markdown V2
        parsing and handles network errors gracefully.

        Args:
            chat (TelegramChat): The target chat for the message.
            message (str): The message content to send.
            reply_markup (Any, optional): Keyboard markup for interactive messages.
        """
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
        """Escape text for Telegram Markdown V2 formatting.

        Args:
            value (str): The text to escape.

        Returns:
            str: The escaped text safe for Markdown V2 parsing.
        """
        return escape_markdown(value, version=2)

    def handle_invalid_token(self, log_error: bool = True) -> None:
        """Handle invalid Telegram Bot token errors.

        Clears the invalid token from settings, resets the cached application,
        and optionally logs the error.

        Args:
            log_error (bool): Whether to log the authentication error. Defaults to True.
        """
        self.settings.secret = None
        self.settings.save(update_fields=["_token"])
        del self.app  # Remove cached_property value, so it will be regenerated
        if log_error:
            self.logger.error("[Telegram] Authentication error")

"""Base framework for Telegram Bot integration with Rekono.

Provides the foundational classes and utilities for Telegram Bot operations
including application management, message handling, and token validation.
"""

import asyncio
from functools import cached_property
from typing import Any

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import Forbidden, InvalidToken, NetworkError
from telegram.ext import Application, CallbackContext
from telegram.helpers import escape_markdown

from framework.logging import LoggingEntity
from platforms.telegram_app.models import TelegramChat, TelegramSettings


class BaseTelegram(LoggingEntity):
    """Base class for Telegram Bot integration with application management.

    Provides core functionality for Telegram Bot operations including application
    initialization, message sending, token validation, and error handling.

    Attributes:
        date_format (str): Date format used for execution timestamps in messages.
        _app (Application | None): Cached Telegram application client.
        _initialized (bool): Whether the bot application has been initialized.
    """

    date_format = "%Y-%m-%d %H:%M:%S %Z"
    _app = None
    _initialized = False

    @cached_property
    def settings(self) -> TelegramSettings:
        """Get Telegram Bot configuration settings from database.

        Returns:
            TelegramSettings: Telegram configuration instance or None if not configured.
        """
        return TelegramSettings.objects.first()

    def initialize(self) -> None:
        """Initialize the Telegram Bot application.

        Runs the bot's async initialization once; the _initialized guard makes
        repeated calls no-ops. Clears the stored token if authentication fails,
        and leaves the bot uninitialized without clearing the token if the
        Telegram API is temporarily unreachable, so a later request can retry.
        """
        if not self._initialized and self.app and self.app.bot:  # pytype: disable=attribute-error
            try:
                asyncio.run(self.app.bot.initialize())  # pytype: disable=attribute-error
                self._initialized = True
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()
            except Exception as ex:
                # The Telegram API is temporarily unreachable
                # Keep the token and leave the bot uninitialized so the next request can retry
                self.logger.error(
                    f"[Telegram] {ex.__class__.__name__} error when trying to initialize the Telegram Bot: {str(ex)}"
                )

    @property
    def app(self) -> Application | None:
        """Get the Telegram Bot application instance.

        Creates and configures the Telegram Bot application using the stored token.

        Returns:
            Application | None: The configured bot application or None if no token.
        """
        if not self._app and self.settings and self.settings.secret:
            try:
                self._app = Application.builder().token(self.settings.secret).post_init(self.post_init).build()
                self._app.add_error_handler(self.handle_error)
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()
        return self._app

    @property
    def bot_name(self) -> str | None:
        """Get the Telegram Bot username.

        The username comes from the get_me call performed during initialization, so it
        is only available once the bot has been initialized. Accessing it beforehand
        would raise a RuntimeError, hence the _initialized guard.

        Returns:
            str | None: The bot username if the bot has been initialized, None otherwise.
        """
        return self.app.bot.username if self._initialized and self.app and self.app.bot else None

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
                asyncio.run(self._send_message(chat, message, reply_markup))
            except NetworkError:
                pass

    async def _send_message(self, chat: TelegramChat, message: str, reply_markup: Any = None) -> None:
        """Send a message with a bot HTTP client bound to the current event loop.

        Each call runs in its own `asyncio.run` loop, so the bot's HTTP client is opened and
        closed within that loop. Reusing it across loops would bind its connection pool to an
        already closed loop, raising "Event loop is closed" and silently dropping notifications.

        Args:
            chat (TelegramChat): The target chat for the message.
            message (str): The message content to send.
            reply_markup (Any, optional): Keyboard markup for interactive messages.
        """
        async with self.app.bot as bot:  # pytype: disable=attribute-error
            await bot.send_message(
                chat.chat_id,
                message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup,
            )

    def escape(self, value: str, entity_type: str | None = None) -> str:
        """Escape text for Telegram Markdown V2 formatting.

        Args:
            value (str): The text to escape.
            entity_type (str | None, optional): Markdown V2 entity the text belongs to. Use
                "text_link" to escape a link URL, where only ")" and "\\" must be escaped instead
                of the full set of special characters. Defaults to None (general text escaping).

        Returns:
            str: The escaped text safe for Markdown V2 parsing.
        """
        return escape_markdown(value, version=2, entity_type=entity_type)

    async def handle_error(self, update: object, context: CallbackContext) -> None:
        """Global error handler for uncaught exceptions raised by bot handlers.

        Registered as the Application's error handler so exceptions raised while
        processing an update (e.g. transient network disconnections) are logged
        instead of being silently dropped by python-telegram-bot with a
        "No error handlers are registered" warning.

        Args:
            update (object): The update that caused the error, if any.
            context (CallbackContext): The callback context holding the raised error.
        """
        if not isinstance(update, Update):
            return
        chat_id = update.effective_chat.id if update.effective_chat else None  # pytype: disable=attribute-error
        self.logger.error(
            f"[Telegram] Unhandled exception while processing update from chat {chat_id}: {context.error}",
            exc_info=context.error,
        )

    def handle_invalid_token(self, log_error: bool = True) -> None:
        """Handle invalid Telegram Bot token errors.

        Clears the invalid token from settings, resets the cached application,
        and optionally logs the error.

        Args:
            log_error (bool): Whether to log the authentication error. Defaults to True.
        """
        self.settings.secret = None
        self.settings.save(update_fields=["_token"])
        self._app = None
        self._initialized = False
        if log_error:
            self.logger.error("[Telegram] Authentication error")

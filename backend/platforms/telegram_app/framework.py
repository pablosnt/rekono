"""Base class shared by the Telegram notifications and the Telegram bot.

Both directions talk to the same bot, so creating it, sending messages, and dealing
with an invalid token are defined once here.
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
    """Telegram bot that Rekono talks to the users through.

    The bot client is created the first time that it's needed, and it's only ready
    once Telegram accepts the configured token.

    Attributes:
        date_format: Format that the dates are written in.
    """

    date_format = "%Y-%m-%d %H:%M:%S %Z"
    _app = None
    _initialized = False

    @cached_property
    def settings(self) -> TelegramSettings:
        """The Telegram configuration, or None if it hasn't been created yet."""
        return TelegramSettings.objects.first()

    def initialize(self) -> None:
        """Prepare the bot client to be used, if it isn't ready yet.

        The token is removed if Telegram rejects it, but it's kept if Telegram
        can't be reached, so the next request can try again.
        """
        if not self._initialized and self.app and self.app.bot:  # pytype: disable=attribute-error
            try:
                asyncio.run(self.app.bot.initialize())  # pytype: disable=attribute-error
                self._initialized = True
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()
            except Exception as ex:
                self.logger.error(
                    f"[Telegram] {ex.__class__.__name__} error when trying to initialize the Telegram Bot: {str(ex)}"
                )

    @property
    def app(self) -> Application | None:
        """The bot client, or None if no bot token is configured."""
        if not self._app and self.settings and self.settings.secret:
            try:
                self._app = Application.builder().token(self.settings.secret).post_init(self.post_init).build()
                self._app.add_error_handler(self.handle_error)
            except (InvalidToken, Forbidden):
                self.handle_invalid_token()
        return self._app

    @property
    def bot_name(self) -> str | None:
        """The name of the bot, or None until its client has been prepared."""
        return self.app.bot.username if self._initialized and self.app and self.app.bot else None

    async def post_init(self, application: Application) -> None:
        """Prepare whatever the bot needs once its client has been created.

        Args:
            application: Bot client that was created.
        """
        pass

    def send_message(self, chat: TelegramChat, message: str, reply_markup: Any = None) -> None:
        """Send a message to a Telegram chat.

        Args:
            chat: Chat where the message is sent.
            message: Content of the message, written in Markdown.
            reply_markup: Buttons that the users can answer the message with.
        """
        if self.app and self.app.bot:
            try:
                asyncio.run(self._send_message(chat, message, reply_markup))
            except NetworkError:
                pass

    async def _send_message(self, chat: TelegramChat, message: str, reply_markup: Any = None) -> None:
        """Send a message with a client bound to the loop that is running now.

        Args:
            chat: Chat where the message is sent.
            message: Content of the message, written in Markdown.
            reply_markup: Buttons that the users can answer the message with.
        """
        # Every call runs its own event loop, so the HTTP client of the bot has to be opened
        # and closed in it: reusing it would bind its connections to a loop that is already
        # closed, and the messages would be dropped
        async with self.app.bot as bot:  # pytype: disable=attribute-error
            await bot.send_message(
                chat.chat_id,
                message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup,
            )

    def escape(self, value: str, entity_type: str | None = None) -> str:
        """Escape a text so Telegram doesn't read it as Markdown.

        Args:
            value: Text to escape.
            entity_type: Kind of Markdown entity that the text belongs to, which
              is only needed for the links, since fewer characters are escaped
              inside a URL.

        Returns:
            The text as Telegram must show it.
        """
        return escape_markdown(value, version=2, entity_type=entity_type)

    async def handle_error(self, update: object, context: CallbackContext) -> None:
        """Log the errors that the bot handlers don't catch themselves.

        Args:
            update: Message that was being processed when the error happened.
            context: Context of the handler, which is where the error is.
        """
        if not isinstance(update, Update):
            return
        chat_id = update.effective_chat.id if update.effective_chat else None  # pytype: disable=attribute-error
        self.logger.error(
            f"[Telegram] Unhandled exception while processing update from chat {chat_id}: {context.error}",
            exc_info=context.error,
        )

    def handle_invalid_token(self, log_error: bool = True) -> None:
        """Remove the bot token that Telegram rejected.

        Args:
            log_error: Whether the rejection must be logged, which it isn't when
              the users are the ones checking if the token works.
        """
        self.settings.secret = None
        self.settings.save(update_fields=["_token"])
        self._app = None
        self._initialized = False
        if log_error:
            self.logger.error("[Telegram] Authentication error")

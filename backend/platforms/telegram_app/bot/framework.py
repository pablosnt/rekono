"""Framework base classes for Telegram Bot command and conversation handling.

Provides abstract base classes for bot commands and conversations with
context management, authentication validation, and message utilities.
"""

from functools import cached_property
from typing import Any

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramChat
from users.models import User


class BaseTelegramBot(BaseTelegram):
    """Base class for Telegram Bot commands and conversations.

    Provides common functionality for bot interactions including context management,
    authentication validation, and message handling utilities.

    Attributes:
        help (str): Help text description for the command or conversation.
        section (None): Section categorization for command organization.
        allow_readers (bool): Whether users with reader permissions can use this command.
        chat (None): Current chat context (set during execution).
    """

    help = ""
    section = None
    allow_readers = False
    chat = None

    @cached_property
    def command_name(self) -> str:
        """Get the lowercase class name as the command name.

        Returns:
            str: The lowercase class name used as the command identifier.
        """
        return self.__class__.__name__.lower()

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Execute the bot command with validation and authentication.

        Template method for command execution. Subclasses should override this
        method to implement specific command logic.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int | None: Conversation state or None for simple commands.
        """
        pass

    def validate_update(self, update: Update) -> None:
        """Validate that the Telegram update contains required information.

        Args:
            update (Update): The Telegram update to validate.

        Raises:
            Exception: If the update lacks required chat or message information.
        """
        if None in [update.effective_chat, update.effective_message]:
            self.logger.error("Invalid provided update")
            raise Exception("Invalid provided update")

    async def reply(self, update: Update, message: str, reply_markup: Any = None) -> None:
        """Reply to a Telegram message with formatted content.

        Sends a reply message with Markdown V2 formatting and optional keyboard markup.

        Args:
            update (Update): The Telegram update to reply to.
            message (str): The message content to send.
            reply_markup (Any, optional): Keyboard markup for interactive replies.
        """
        await update.effective_message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

    def get_context_value(self, context: CallbackContext, key: Context) -> Any:
        """Get a value from the conversation context.

        Args:
            context (CallbackContext): The callback context containing chat data.
            key (Context): The context key to retrieve.

        Returns:
            Any: The stored context value or None if not found.
        """
        return (context.chat_data or {}).get(key.value)

    def add_context_value(self, context: CallbackContext, key: Context, value: Any) -> None:
        """Add a value to the conversation context.

        Safely stores a value in the conversation context only if chat_data is available.

        Args:
            context (CallbackContext): The callback context to update.
            key (Context): The context key to set.
            value (Any): The value to store.
        """
        if context.chat_data is not None:
            context.chat_data[key.value] = value

    def remove_context_value(self, context: CallbackContext, key: Context) -> None:
        """Remove a value from the conversation context.

        Args:
            context (CallbackContext): The callback context to update.
            key (Context): The context key to remove.
        """
        if context.chat_data and key.value in context.chat_data:
            context.chat_data.pop(key.value)

    def remove_all_context_values(self, context: CallbackContext) -> None:
        """Remove all context values except the project context.

        Clears all conversation context data while preserving the project context
        which is needed for continued operations.

        Args:
            context (CallbackContext): The callback context to clear.
        """
        for key in Context:
            if key != Context.PROJECT:
                self.remove_context_value(context, key)

    @sync_to_async
    def _get_active_telegram_chat_async(self, chat_id: int) -> TelegramChat:
        """Get active Telegram chat by ID (async wrapper).

        Args:
            chat_id (int): The Telegram chat ID to search for.

        Returns:
            TelegramChat: The active Telegram chat instance or None.
        """
        return TelegramChat.objects.filter(chat_id=chat_id, user__is_active=True).first()

    @sync_to_async
    def is_auditor_async(self, telegram_chat: TelegramChat) -> bool:
        """Check if chat user has auditor permissions (async wrapper).

        Args:
            telegram_chat (TelegramChat): The Telegram chat to check.

        Returns:
            bool: True if the user has auditor or admin permissions.
        """
        return telegram_chat.is_auditor()

    async def log_command_execution(
        self, update: Update, command_name: str, user: User | None = None
    ) -> None:
        """Log the execution of a Telegram bot command for audit purposes.

        Records the chat where the command was executed and, when known, the
        user that ran it. Callers that already resolved the chat's user (e.g.
        via get_active_telegram_chat) should pass it in to avoid an extra
        lookup; otherwise it's resolved from the update, falling back to
        logging the user as anonymous when the chat isn't linked to anyone.

        Args:
            update (Update): The Telegram update containing the command.
            command_name (str): The name of the command being executed.
            user (User | None, optional): The user that triggered the command,
                if already known.
        """
        if update.effective_chat is None:
            return
        if user is None:
            chat = await self._get_active_telegram_chat_async(update.effective_chat.id)
            user = chat.user if chat else None
        self.logger.info(
            f"[TelegramBot] Command /{command_name} executed in chat {update.effective_chat.id} "
            f"by user {user.id if user else 'anonymous'}",
            extra={"user": user.id} if user else {},
        )

    async def get_active_telegram_chat(self, update: Update) -> TelegramChat | None:
        """Get and validate the active Telegram chat for the update.

        Retrieves the chat associated with the update and validates authentication
        and authorization permissions.

        Args:
            update (Update): The Telegram update containing chat information.

        Returns:
            TelegramChat | None: The authenticated chat or None if validation fails.
        """
        self.validate_update(update)
        chat = await self._get_active_telegram_chat_async(update.effective_chat.id)
        if not chat:
            self.logger.error(f"[Security] Unauthenticated Telegram bot request from chat {update.effective_chat.id}")
            await self.reply(
                update,
                "You have to link this chat to your Rekono account before using the Telegram Bot\. Use the command /start",
            )
        elif not self.allow_readers and not await self.is_auditor_async(chat):
            self.logger.error(
                f"[Security] User {chat.user.id} isn't authorized to use Telegram bot", extra={"user": chat.user}
            )
            await self.reply(update, f"You are not authorized to run /{self.command_name}")
        return chat

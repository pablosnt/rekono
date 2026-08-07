"""Base class shared by all the bot commands and conversations.

Everything that the commands need to do before answering, like knowing which user
is writing and remembering what a conversation already asked, is defined here.
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
    """Base command that the bot answers to.

    Attributes:
        help: Description of the command, shown in the help and in Telegram.
        section: Group of the help message that the command belongs to.
        allow_readers: Whether the users that can only read data can run the
          command, which is false for everything that creates or runs something.
        chat: Chat that is running the command.
    """

    help = ""
    section = None
    allow_readers = False
    chat = None

    @cached_property
    def command_name(self) -> str:
        """The name of the command, which is the class name in lowercase."""
        return self.__class__.__name__.lower()

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Answer the command.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next question of the conversation, or None if the command is
            answered with a single message.
        """
        pass

    def validate_update(self, update: Update) -> None:
        """Check that a message comes from a chat and has content.

        Args:
            update: Message that the user wrote.

        Raises:
            Exception: If the message has no chat or no content, which shouldn't
              happen and means that something is wrong with the update.
        """
        if None in [update.effective_chat, update.effective_message]:
            self.logger.error("Invalid provided update")
            raise Exception("Invalid provided update")

    async def reply(self, update: Update, message: str, reply_markup: Any = None) -> None:
        """Answer a message that a user wrote.

        Args:
            update: Message to answer.
            message: Content of the answer, written in Markdown.
            reply_markup: Buttons that the users can answer with.
        """
        await update.effective_message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

    def get_context_value(self, context: CallbackContext, key: Context) -> Any:
        """Get something that the conversation already asked for.

        Args:
            context: Data that the conversation remembers.
            key: Kind of data to get.

        Returns:
            The data, or None if the conversation hasn't asked for it yet.
        """
        return (context.chat_data or {}).get(key.value)

    def add_context_value(self, context: CallbackContext, key: Context, value: Any) -> None:
        """Remember something that the conversation just asked for.

        Args:
            context: Data that the conversation remembers.
            key: Kind of data to remember.
            value: Data to remember.
        """
        if context.chat_data is not None:
            context.chat_data[key.value] = value

    def remove_context_value(self, context: CallbackContext, key: Context) -> None:
        """Forget something that the conversation asked for.

        Args:
            context: Data that the conversation remembers.
            key: Kind of data to forget.
        """
        if context.chat_data and key.value in context.chat_data:
            context.chat_data.pop(key.value)

    def remove_all_context_values(self, context: CallbackContext) -> None:
        """Forget everything that a conversation asked for, except the project.

        Args:
            context: Data that the conversation remembers.
        """
        for key in Context:
            if key != Context.PROJECT:
                self.remove_context_value(context, key)

    @sync_to_async
    def _get_active_telegram_chat_async(self, chat_id: int) -> TelegramChat:
        """Get the chat with an identifier, if it belongs to an active user.

        Args:
            chat_id: Identifier that Telegram gives to the conversation.

        Returns:
            The chat, or None when it isn't linked to any account or its user was
            disabled, so a disabled user can't keep using the bot.
        """
        # select_related caches the user so later user access doesn't trigger a lazy query outside this sync context
        return TelegramChat.objects.select_related("user").filter(chat_id=chat_id, user__is_active=True).first()

    @sync_to_async
    def is_auditor_async(self, telegram_chat: TelegramChat) -> bool:
        """Check if the user of a chat can do more than read the data.

        Args:
            telegram_chat: Chat whose user roles are checked.

        Returns:
            Whether the user has the Auditor or the Admin role.
        """
        return telegram_chat.is_auditor()

    async def log_command_execution(self, update: Update, command_name: str, user: User | None = None) -> None:
        """Log that a command was run, and who ran it.

        Args:
            update: Message that the user wrote.
            command_name: Name of the command that was run.
            user: User that ran it, if the caller already knows who they are,
              since it has to be searched otherwise.
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
        """Get the chat that is running a command, if it's allowed to run it.

        A chat is linked to a Rekono account instead of logging in, so a chat that
        isn't linked to an active user can't run anything.

        Args:
            update: Message that the user wrote.

        Returns:
            The chat, or None if it isn't linked to an active user or if that user
            isn't allowed to run this command. The user is told why in both cases.
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
            return None
        return chat

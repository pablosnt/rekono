"""Bot commands that are answered with a single message."""

from typing import Any

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

from framework.logging import LoggingEntity
from platforms.telegram_app.bot.enums import Context, Section
from platforms.telegram_app.bot.framework import BaseTelegramBot
from platforms.telegram_app.models import TelegramChat
from rekono.settings import DESCRIPTION
from security.cryptography import Crypto
from users.models import User


class BaseCommand(CommandHandler, BaseTelegramBot, LoggingEntity):
    """Base command that the users run by writing its name in the chat."""

    def __init__(self, **kwargs: Any) -> None:
        """Prepare the command to be registered in the bot.

        Args:
            **kwargs: Not used, since a command is always built from its own name
              and from its own answer.
        """
        super().__init__(command=self.command_name, callback=self.execute_command)

    async def execute_command(self, update: Update, context: CallbackContext) -> None | int:
        """Answer the command, logging whatever goes wrong.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next question of the conversation, or None if the command is
            answered with a single message or if answering it failed.
        """
        try:
            # Propagate the return value not to break conversations flow
            return await self._execute_command(update, context)
        except Exception as ex:
            self.logger.error(
                f"[{self.__class__.__name__}] Error executing Telegram Bot command /{self.command_name}: {str(ex)}"
            )


class Help(BaseCommand):
    """Command that tells the users what the bot can do.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
        allow_readers: Everybody can ask for help.
        bot_commands: Commands that the help message describes, sorted by section.
    """

    help = "Show this message"
    section = Section.BASIC
    allow_readers = True

    def __init__(self, commands: list[BaseTelegramBot]) -> None:
        """Prepare the command with the commands that it has to describe.

        Args:
            commands: Commands of the bot, without this one.
        """
        self.bot_commands = commands + [self]
        self.bot_commands.sort(key=lambda c: c.section.value)
        super().__init__()

    def _build_help_message(self, commands: list[BaseTelegramBot]) -> str:
        """Write the help message, with the commands grouped by their section.

        Args:
            commands: Commands to describe.

        Returns:
            The message, escaped so Telegram doesn't read it as Markdown.
        """
        message = f"{self.escape(DESCRIPTION)}\n"
        current_section = None
        for command in commands:
            if command.section != current_section:
                current_section = command.section
                message += f"\n*{current_section.value}*\n"
            message += f"/{command.command_name} \- {self.escape(command.help)}\n"
        return message

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Answer with the commands that the user can run.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            None, since the command is answered with a single message instead of
            starting a conversation.
        """
        chat = await self.get_active_telegram_chat(update)
        await self.log_command_execution(update, self.command_name, chat.user if chat else None)
        if chat:
            await self.reply(
                update,
                self._build_help_message(
                    self.bot_commands
                    if await self.is_auditor_async(chat)
                    else [c for c in self.bot_commands if c.allow_readers]
                ),
            )


class Start(BaseCommand):
    """Command that gives the code needed to link the chat to an account.

    The bot never links the chat itself, the users have to redeem the code in
    Rekono, so nobody can link a chat to an account that isn't theirs.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
        allow_readers: Everybody can link their chat.
    """

    help = "Initialize the Rekono bot"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _update_or_create_telegram_chat_async(self, chat_id: int) -> tuple[TelegramChat, str]:
        """Give a chat a new code to be linked with.

        Args:
            chat_id: Identifier that the chat has in Telegram.

        Returns:
            The chat and the code that the user has to redeem in Rekono, which is
            only stored as a hash.
        """
        plain_otp = User.objects.generate_otp(TelegramChat)
        telegram_chat, _ = TelegramChat.objects.update_or_create(
            defaults={
                "user": None,
                "otp": Crypto.hash(plain_otp),
                "otp_expiration": User.objects.get_otp_expiration_time(),
            },
            chat_id=chat_id,
        )
        return telegram_chat, plain_otp

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Answer with the code that links the chat to a Rekono account.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            None, since the command is answered with a single message instead of
            starting a conversation.
        """
        self.validate_update(update)
        await self.log_command_execution(update, self.command_name)
        # Only issue account-linking OTPs in private chats. In a group/supergroup/channel the token
        # would be visible to every member, letting anyone bind the shared chat to their own account
        # and receive that user's notifications and command output.
        if update.effective_chat.type != ChatType.PRIVATE:
            self.logger.warning(
                f"[Security] Rejected Telegram /start account-linking from non-private chat {update.effective_chat.id}"
            )
            await self.reply(
                update,
                "Account linking is only available in private chats\. Please, send a direct message to the bot and run /start there",
            )
            return
        telegram_chat, plain_otp = await self._update_or_create_telegram_chat_async(update.effective_chat.id)
        self.logger.info(f"[Security] New login request using the Telegram bot from the chat {telegram_chat.chat_id}")
        await self.reply(
            update,
            """
*Welcome to Rekono Bot\!*

Link this chat with your Rekono account by adding the following token to your Rekono profile:

`{otp}`

Then, run /help to start hacking\!
""".format(otp=plain_otp),
        )


class Logout(BaseCommand):
    """Command that unlinks the chat from the account that it belongs to.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
        allow_readers: Everybody can unlink their chat.
    """

    help = "Unlink bot from your account"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _logout_user_in_telegram_async(self, chat_id: int) -> None:
        """Remove a chat, so it has to be linked again to be used.

        Args:
            chat_id: Identifier that the chat has in Telegram.
        """
        chat = TelegramChat.objects.filter(chat_id=chat_id).first()
        if chat:
            if chat.user:
                self.logger.info(
                    f"[Security] User {chat.user.id} has logged out from the Telegram bot", extra={"user": chat.user}
                )
            chat.delete()

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Unlink the chat and say goodbye.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            None, since the command is answered with a single message instead of
            starting a conversation.
        """
        self.validate_update(update)
        await self.log_command_execution(update, self.command_name)
        await self._logout_user_in_telegram_async(update.effective_chat.id)
        await self.reply(update, "Bye\!")


class Cancel(BaseCommand):
    """Command that stops the conversation that the user is having with the bot.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
    """

    help = "Cancel current operation"
    section = Section.BASIC

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Forget what the conversation asked for and end it.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The end of the conversation.
        """
        self.validate_update(update)
        await self.log_command_execution(update, self.command_name)
        self.remove_all_context_values(context)
        await self.reply(update, "Operation has been cancelled")
        return ConversationHandler.END


class SelectionCommands(BaseCommand):
    """Base command that works with the project that the chat is using.

    Attributes:
        section: Group of the help message that these commands belong to.
    """

    section = Section.PROJECTS


class ShowProject(SelectionCommands):
    """Command that says which project the chat is using.

    Attributes:
        help: Description of the command.
    """

    help = "Select one project to be used in next commands"

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Answer with the project that the chat is using.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            None, since the command is answered with a single message instead of
            starting a conversation.
        """
        self.validate_update(update)
        await self.log_command_execution(update, self.command_name)
        project = self.get_context_value(context, Context.PROJECT)
        if project:
            await self.reply(update, f"💼 _Project_   *{self.escape(project.name)}*")
        else:
            await self.reply(update, "No selected project\. Use the command /selectproject")


class ClearProject(SelectionCommands):
    """Command that forgets the project that the chat is using.

    Attributes:
        help: Description of the command.
    """

    help = "Clear project selection"

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Forget the project that the chat is using.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            None, since the command is answered with a single message instead of
            starting a conversation.
        """
        self.validate_update(update)
        await self.log_command_execution(update, self.command_name)
        self.remove_context_value(context, Context.PROJECT)
        await self.reply(update, "Project selection has been cleared")

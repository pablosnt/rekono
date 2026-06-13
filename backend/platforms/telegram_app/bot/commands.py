"""Telegram Bot command implementations for security testing operations.

Provides basic bot commands for user authentication, help system, and
project management through simple command interactions.
"""

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
    """Base class for Telegram Bot commands.

    Combines CommandHandler functionality with bot framework capabilities
    to provide a foundation for implementing bot commands with error handling
    and logging support.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the base command with command name and callback.

        Args:
            **kwargs: Additional keyword arguments for the CommandHandler.
        """
        super().__init__(command=self.command_name, callback=self.execute_command)

    async def execute_command(self, update: Update, context: CallbackContext) -> None | int:
        """Execute the command with error handling.

        Wrapper method that calls the actual command implementation with
        exception handling to prevent bot crashes.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            None | int: Command result or conversation state.
        """
        try:
            await self._execute_command(update, context)
        except Exception:
            pass


class Help(BaseCommand):
    """Help command for displaying available bot commands and usage information.

    Provides comprehensive help system showing all available commands organized
    by sections with descriptions and usage information.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (BASIC).
        allow_readers (bool): Allow users with reader permissions to use this command.
    """

    help = "Show this message"
    section = Section.BASIC
    allow_readers = True

    def __init__(self, commands: list[BaseTelegramBot]) -> None:
        """Initialize the help command with a list of available commands.

        Args:
            commands (list[BaseTelegramBot]): List of bot commands to include in help.
        """
        self.bot_commands = commands + [self]
        self.bot_commands.sort(key=lambda c: c.section.value)
        super().__init__()

    def _build_help_message(self, commands: list[BaseTelegramBot]) -> str:
        """Build formatted help message with commands organized by section.

        Args:
            commands (list[BaseTelegramBot]): List of commands to include in help.

        Returns:
            str: Formatted help message with escaped Markdown content.
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
        """Execute the help command showing available commands.

        Displays different command sets based on user permissions (auditor vs reader).

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int | None: None for simple command execution.
        """
        # await super().execute_command(update, context)
        chat = await self.get_active_telegram_chat(update)
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
    """Start command for initializing bot and generating account linking tokens.

    Generates One-Time Passwords (OTP) for linking Telegram chats with Rekono
    user accounts, enabling secure authentication and authorization.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (BASIC).
        allow_readers (bool): Allow users with reader permissions to use this command.
    """

    help = "Initialize the Rekono bot"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _update_or_create_telegram_chat_async(self, chat_id: int) -> tuple[TelegramChat, str]:
        """Create or update Telegram chat with new OTP for account linking.

        Args:
            chat_id (int): The Telegram chat ID to create or update.

        Returns:
            tuple[TelegramChat, str]: The chat instance and plain text OTP.
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
        """Execute the start command to generate account linking token.

        Only runs in private chats. In a group or channel the request is rejected
        so the linking token is never exposed to other members.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int | None: None for simple command execution.
        """
        self.validate_update(update)
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
    """Logout command for unlinking Telegram chat from user account.

    Removes the association between a Telegram chat and user account,
    effectively logging the user out from the bot.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (BASIC).
        allow_readers (bool): Allow users with reader permissions to use this command.
    """

    help = "Unlink bot from your account"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _logout_user_in_telegram_async(self, chat_id: int) -> None:
        """Remove Telegram chat and log user logout.

        Args:
            chat_id (int): The Telegram chat ID to remove.
        """
        chat = TelegramChat.objects.filter(chat_id=chat_id).first()
        if chat:
            if chat.user:
                self.logger.info(
                    f"[Security] User {chat.user.id} has logged out from the Telegram bot", extra={"user": chat.user}
                )
            chat.delete()

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Execute the logout command to unlink the chat.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int | None: None for simple command execution.
        """
        # await super().execute_command(update, context)
        self.validate_update(update)
        await self._logout_user_in_telegram_async(update.effective_chat.id)
        await self.reply(update, "Bye\!")


class Cancel(BaseCommand):
    """Cancel command for terminating ongoing conversations and operations.

    Cancels any active conversation or operation and clears the conversation
    context, returning the user to the main bot interface.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (BASIC).
    """

    help = "Cancel current operation"
    section = Section.BASIC

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Execute the cancel command to end conversations.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int: ConversationHandler.END to terminate conversations.
        """
        # await super().execute_command(update, context)
        self.validate_update(update)
        self.remove_all_context_values(context)
        await self.reply(update, "Operation has been cancelled")
        return ConversationHandler.END


class SelectionCommands(BaseCommand):
    """Base class for project-related commands.

    Abstract base class for commands that handle project operations
    such as project selection and context management.

    Attributes:
        section (Section): Command section for organization (PROJECTS).
    """

    section = Section.PROJECTS


class ShowProject(SelectionCommands):
    """Command for displaying the currently selected project.

    Shows the project currently stored in the conversation context,
    or prompts to select a project if none is selected.

    Attributes:
        help (str): Command help text displayed in command list.
    """

    help = "Select one project to be used in next commands"

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Execute the show project command.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int | None: None for simple command execution.
        """
        # await super().execute_command(update, context)
        self.validate_update(update)
        project = self.get_context_value(context, Context.PROJECT)
        if project:
            await self.reply(update, f"💼 _Project_   *{self.escape(project.name)}*")
        else:
            await self.reply(update, "No selected project\. Use the command /selectproject")


class ClearProject(SelectionCommands):
    """Command for clearing the currently selected project from context.

    Removes the project selection from the conversation context,
    requiring the user to select a new project for subsequent operations.

    Attributes:
        help (str): Command help text displayed in command list.
    """

    help = "Clear project selection"

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        """Execute the clear project command.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the command.

        Returns:
            int | None: None for simple command execution.
        """
        # await super().execute_command(update, context)
        self.validate_update(update)
        self.remove_context_value(context, Context.PROJECT)
        await self.reply(update, "Project selection has been cleared")

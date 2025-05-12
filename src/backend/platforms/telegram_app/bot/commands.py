import logging
from typing import Any

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

from platforms.telegram_app.bot.enums import Context, Section
from platforms.telegram_app.bot.framework import BaseTelegramBot
from platforms.telegram_app.models import TelegramChat
from rekono.settings import DESCRIPTION
from security.cryptography.hashing import hash
from users.models import User

logger = logging.getLogger()


class BaseCommand(CommandHandler, BaseTelegramBot):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(command=self.get_name(), callback=self.execute_command)

    async def execute_command(self, update: Update, context: CallbackContext) -> None | int:
        try:
            await self._execute_command(update, context)
        except Exception:  # nosec
            pass


class Help(BaseCommand):
    help = "Show this message"
    section = Section.BASIC
    allow_readers = True

    def __init__(self, commands: list[BaseTelegramBot]) -> None:
        self.bot_commands = commands + [self]
        self.bot_commands.sort(key=lambda c: c.section.value)
        super().__init__()

    def _build_help_message(self, commands: list[BaseTelegramBot]) -> str:
        message = f"{self._escape(DESCRIPTION)}\n"
        current_section = None
        for command in commands:
            if command.section != current_section:
                current_section = command.section
                message += f"\n*{current_section.value}*\n"
            message += f"/{command.get_name()} \- {self._escape(command.help)}\n"
        return message

    async def _execute_command(self, update: Update, context: CallbackContext) -> None:
        await super()._execute_command(update, context)
        chat = await self._get_active_telegram_chat(update)
        if chat:
            await self._reply(
                update,
                self._build_help_message(
                    self.bot_commands
                    if await self._is_auditor_async(chat)
                    else [c for c in self.bot_commands if c.allow_readers]
                ),
            )


class Start(BaseCommand):
    help = "Initialize the Rekono bot"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _update_or_create_telegram_chat_async(self, chat_id: int) -> tuple[TelegramChat | str]:
        plain_otp = User.objects.generate_otp(TelegramChat)
        telegram_chat, _ = TelegramChat.objects.update_or_create(
            defaults={
                "user": None,
                "otp": hash(plain_otp),
                "otp_expiration": User.objects.get_otp_expiration_time(),
            },
            chat_id=chat_id,
        )
        return telegram_chat, plain_otp

    async def _execute_command(self, update: Update, context: CallbackContext) -> None:
        await super()._execute_command(update, context)
        telegram_chat, plain_otp = await self._update_or_create_telegram_chat_async(update.effective_chat.id)
        logger.info(f"[Security] New login request using the Telegram bot from the chat {telegram_chat.chat_id}")
        await self._reply(
            update,
            """
*Welcome to Rekono Bot\!*

Link this chat with your Rekono account by adding the following token to your Rekono profile:

`{otp}`

Then, type /help to start hacking\. Enjoy\!
""".format(otp=plain_otp),
        )


class Logout(BaseCommand):
    help = "Unlink bot from your account"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _logout_user_in_telegram_async(self, chat_id: int) -> None:
        chat = TelegramChat.objects.filter(chat_id=chat_id).first()
        if chat:
            if chat.user:
                logger.info(
                    f"[Security] User {chat.user.id} has logged out from the Telegram bot",
                    extra={"user": chat.user},
                )
            chat.delete()

    async def _execute_command(self, update: Update, context: CallbackContext) -> None:
        await super()._execute_command(update, context)
        await self._logout_user_in_telegram_async(update.effective_chat.id)
        await self._reply(update, "Bye\!")


class Cancel(BaseCommand):
    help = "Cancel current operation"
    section = Section.BASIC

    async def _execute_command(self, update: Update, context: CallbackContext) -> int:
        await super()._execute_command(update, context)
        self._remove_all_context_values(context)
        await self._reply(update, "Operation has been cancelled")
        return ConversationHandler.END


class SelectionCommands(BaseCommand):
    section = Section.SELECTION


class ShowProject(SelectionCommands):
    help = "Select one project to be used in next commands"

    async def _execute_command(self, update: Update, context: CallbackContext) -> None:
        await super()._execute_command(update, context)
        project = self._get_context_value(context, Context.PROJECT)
        if project:
            await self._reply(
                update,
                f"💼 _Project_   *{self._escape(project.name)}*",
            )
        else:
            await self._reply(update, "No selected project\. Use the command /selectproject")


class ClearProject(SelectionCommands):
    help = "Clear project selection"

    async def _execute_command(self, update: Update, context: CallbackContext) -> None:
        await super()._execute_command(update, context)
        self._remove_context_value(context, Context.PROJECT)
        await self._reply(update, "Project selection has been cleared")

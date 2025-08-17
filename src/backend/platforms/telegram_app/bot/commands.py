from typing import Any

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

from framework.logging import LoggingEntity
from platforms.telegram_app.bot.enums import Context, Section
from platforms.telegram_app.bot.framework import BaseTelegramBot
from platforms.telegram_app.models import TelegramChat
from rekono.settings import DESCRIPTION
from security.cryptography import Crypto
from users.models import User


class BaseCommand(CommandHandler, BaseTelegramBot, LoggingEntity):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(command=self.name, callback=self.execute_command)

    async def execute_command(self, update: Update, context: CallbackContext) -> None | int:
        try:
            await self._execute_command(update, context)
        except Exception:
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
        message = f"{self.escape(DESCRIPTION)}\n"
        current_section = None
        for command in commands:
            if command.section != current_section:
                current_section = command.section
                message += f"\n*{current_section.value}*\n"
            message += f"/{command.name} \- {self.escape(command.help)}\n"
        return message

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
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
    help = "Initialize the Rekono bot"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _update_or_create_telegram_chat_async(self, chat_id: int) -> tuple[TelegramChat, str]:
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
        # await super().execute_command(update, context)
        self.validate_update(update)
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
    help = "Unlink bot from your account"
    section = Section.BASIC
    allow_readers = True

    @sync_to_async
    def _logout_user_in_telegram_async(self, chat_id: int) -> None:
        chat = TelegramChat.objects.filter(chat_id=chat_id).first()
        if chat:
            if chat.user:
                self.logger.info(
                    f"[Security] User {chat.user.id} has logged out from the Telegram bot", extra={"user": chat.user}
                )
            chat.delete()

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        # await super().execute_command(update, context)
        self.validate_update(update)
        await self._logout_user_in_telegram_async(update.effective_chat.id)
        await self.reply(update, "Bye\!")


class Cancel(BaseCommand):
    help = "Cancel current operation"
    section = Section.BASIC

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        # await super().execute_command(update, context)
        self.validate_update(update)
        self.remove_all_context_values(context)
        await self.reply(update, "Operation has been cancelled")
        return ConversationHandler.END


class SelectionCommands(BaseCommand):
    section = Section.SELECTION


class ShowProject(SelectionCommands):
    help = "Select one project to be used in next commands"

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        # await super().execute_command(update, context)
        self.validate_update(update)
        project = self.get_context_value(context, Context.PROJECT)
        if project:
            await self.reply(update, f"💼 _Project_   *{self.escape(project.name)}*")
        else:
            await self.reply(update, "No selected project\. Use the command /selectproject")


class ClearProject(SelectionCommands):
    help = "Clear project selection"

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        # await super().execute_command(update, context)
        self.validate_update(update)
        self.remove_context_value(context, Context.PROJECT)
        await self.reply(update, "Project selection has been cleared")

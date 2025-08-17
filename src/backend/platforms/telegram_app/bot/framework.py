from functools import cached_property
from typing import Any

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramChat


class BaseTelegramBot(BaseTelegram):
    help = ""
    section = None
    allow_readers = False
    chat = None

    @cached_property
    def name(self) -> str:
        return self.__class__.__name__.lower()

    async def _execute_command(self, update: Update, context: CallbackContext) -> int | None:
        # TODO: Ensure that these checks are no longer needed:
        # if not self._is_valid_update(update):
        #     raise Exception("Invalid update")
        # if not self.allow_readers:
        #     chat = await self.get_active_telegram_chat(update)
        #     if not chat:
        #         raise Exception("User is not authenticated")
        # TODO: So, ensure that it's not needed to call super()._execute_command in each subclass
        pass

    def validate_update(self, update: Update) -> None:
        if None in [update.effective_chat, update.effective_message]:
            self.logger.error("Invalid provided update")
            raise Exception("Invalid provided update")

    async def reply(self, update: Update, message: str, reply_markup: Any = None) -> None:
        # TODO: Validate that this is no longer needed. Update should have been validated before
        # if self.is_valid_update(update):
        await update.effective_message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

    def get_context_value(self, context: CallbackContext, key: Context) -> Any:
        return (context.chat_data or {}).get(key.value)

    def add_context_value(self, context: CallbackContext, key: Context, value: Any) -> None:
        if context.chat_data:
            context.chat_data[key.value] = value

    def remove_context_value(self, context: CallbackContext, key: Context) -> None:
        if context.chat_data and key.value in context.chat_data:
            context.chat_data.pop(key.value)

    def remove_all_context_values(self, context: CallbackContext) -> None:
        for key in Context:
            if key != Context.PROJECT:
                self.remove_context_value(context, key)

    @sync_to_async
    def _get_active_telegram_chat_async(self, chat_id: int) -> TelegramChat:
        return TelegramChat.objects.filter(chat_id=chat_id, user__is_active=True).first()

    @sync_to_async
    def is_auditor_async(self, telegram_chat: TelegramChat) -> bool:
        return telegram_chat.is_auditor()

    async def get_active_telegram_chat(self, update: Update) -> TelegramChat | None:
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
            await self.reply(update, f"You are not authorized to run /{self.name}")
        return chat

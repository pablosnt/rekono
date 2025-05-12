import logging
from typing import Any

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramChat

logger = logging.getLogger()


class BaseTelegramBot(BaseTelegram):
    help = ""
    section = None
    allow_readers = False
    chat = None

    def get_name(self) -> str:
        return self.__class__.__name__.lower()

    async def _execute_command(self, update: Update, context: CallbackContext) -> None:
        if not self._is_valid_update(update):
            raise Exception("Invalid update")
        if not self.allow_readers:
            chat = await self._get_active_telegram_chat(update)
            if not chat:
                raise Exception("User is not authenticated")

    def _is_valid_update(self, update: Update) -> bool:
        return update.effective_chat is not None and update.effective_message is not None

    async def _reply(self, update: Update, message: str, reply_markup: Any = None) -> None:
        if self._is_valid_update(update):
            await update.effective_message.reply_text(
                message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2
            )

    def _get_context_value(self, context: CallbackContext, key: str) -> Any:
        return (context.chat_data or {}).get(key)

    def _add_context_value(self, context: CallbackContext, key: str, value: Any) -> None:
        if context.chat_data:
            context.chat_data[key] = value

    def _remove_context_value(self, context: CallbackContext, key: Context) -> None:
        if context.chat_data and key.value in context.chat_data:
            context.chat_data.pop(key.value)

    def _remove_all_context_values(self, context: CallbackContext) -> None:
        for key in Context:
            if key != Context.PROJECT:
                self._remove_context_value(context, key)

    @sync_to_async
    def _get_active_telegram_chat_async(self, chat_id: int) -> TelegramChat:
        return TelegramChat.objects.filter(chat_id=chat_id, user__is_active=True).first()

    @sync_to_async
    def _is_auditor_async(self, telegram_chat: TelegramChat) -> bool:
        return telegram_chat.is_auditor()

    async def _get_active_telegram_chat(self, update: Update, require_auditor: bool = True) -> TelegramChat | None:
        if self.chat:
            return self.chat
        if self._is_valid_update(update):
            self.chat = await self._get_active_telegram_chat_async(update.effective_chat.id)
            if not self.chat:
                logger.error(f"[Security] Unauthenticated Telegram bot request from chat {update.effective_chat.id}")
                await self._reply(
                    update,
                    "You have to link this chat to your Rekono account before using the Telegram Bot\. Use the command /start",
                )
            elif require_auditor and not await self._is_auditor_async(self.chat):
                logger.error(
                    f"[Security] User {self.chat.user.id} isn't authorized to use Telegram bot",
                    extra={"user": self.chat.user},
                )
                await self._reply(update, "You are not authorized to perform this action")
                self.chat = None
            return self.chat

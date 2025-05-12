import logging
from typing import Any, Callable

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import QuerySet
from rest_framework.serializers import Serializer
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.framework import BaseTelegramBot
from platforms.telegram_app.models import TelegramChat

logger = logging.getLogger()


class BaseMixin(BaseTelegramBot):
    def _get_current_state(self, method: Callable) -> int:
        if not hasattr(self, "_states_methods"):
            return ConversationHandler.END
        return self._states_methods.index(method)

    def _get_next_state(self, method: Callable) -> int:
        current_state = self._get_current_state(method)
        return ConversationHandler.END if current_state == len(self._states_methods) - 1 else current_state + 1

    def _get_previous_state(self, method: Callable) -> int:
        current_state = self._get_current_state(method)
        return current_state if current_state == 0 else current_state - 1

    async def _go_to_next_state(self, update: Update, context: CallbackContext, next_state: int) -> int:
        if next_state != ConversationHandler.END and (
            self._states_methods[next_state].__name__.startswith("_ask_for_")
            or self._states_methods[next_state].__name__.startswith("_reply")
        ):
            return await self._states_methods[next_state](update, context)
        return next_state

    @sync_to_async
    def _is_queryset_async(self, queryset: QuerySet) -> bool:
        return bool(queryset)

    @sync_to_async
    def _queryset_exists_async(self, queryset: QuerySet) -> bool:
        return queryset.exists()

    @sync_to_async
    def _get_model_instance_async(self, model: Any, pk: int) -> Any:
        return model.objects.get(pk=pk)

    @sync_to_async
    def _get_keyboard_from_queryset_async(self, queryset: QuerySet, attribute: str) -> QuerySet:
        return [InlineKeyboardButton(getattr(i, attribute), callback_data=i.id) for i in queryset.order_by(attribute)]

    @sync_to_async
    def _save_serializer_async(self, serializer: Serializer) -> tuple[Any | None, dict[str, Any]]:
        try:
            return (serializer.save(), {}) if serializer.is_valid() else (None, serializer.errors)
        except IntegrityError:
            return None, {serializer.Meta.model.__name__.lower(): ["This entity already exists in the database"]}

    async def _ask(
        self,
        update: Update,
        queryset: QuerySet,
        attribute: str,
        options_per_row: int,
        message: str,
        not_found_message: str,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        chat = chat or await self._get_active_telegram_chat(update)
        if not chat or not await self._is_queryset_async(queryset):
            await self._reply(update, not_found_message)
            return ConversationHandler.END
        else:
            keyboard = await self._get_keyboard_from_queryset_async(queryset, attribute)
            await self._reply(
                update,
                message,
                reply_markup=InlineKeyboardMarkup(
                    [keyboard[item : item + options_per_row] for item in range(0, len(keyboard), options_per_row)]
                ),
            )
            return next_state

    async def _ask_values(
        self,
        update: Update,
        values: list[str],
        options_per_row: int,
        message: str,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        chat = chat or await self._get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        keyboard = [InlineKeyboardButton(v.capitalize(), callback_data=v) for v in values]
        await self._reply(
            update,
            message,
            reply_markup=InlineKeyboardMarkup(
                [keyboard[item : item + options_per_row] for item in range(0, len(keyboard), options_per_row)]
            ),
        )
        return next_state

    async def _save(
        self,
        update: Update,
        context: CallbackContext,
        context_key: Context,
        model: Any,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        chat = chat or await self._get_active_telegram_chat(update)
        if chat and update.callback_query and update.callback_query.data:
            entity = await self._get_model_instance_async(model, int(update.callback_query.data))
            self._add_context_value(context, context_key, entity)
            await update.callback_query.answer(f"{model.__name__} {update.callback_query.data} has been selected")
            return next_state
        elif update.callback_query:
            await update.callback_query.answer()
        return ConversationHandler.END

    async def _save_value(
        self,
        update: Update,
        context: CallbackContext,
        context_key: Context,
        name: str,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        chat = chat or await self._get_active_telegram_chat(update)
        if chat and update.callback_query and update.callback_query.data:
            self._add_context_value(context, context_key, update.callback_query.data)
            await update.callback_query.answer(f"{name} {update.callback_query.data} has been selected")
            return next_state
        elif update.callback_query:
            await update.callback_query.answer()
        return ConversationHandler.END

    def _build_error_message_from_serializer_errors(self, serializer_errors: dict[str, Any]) -> str:
        return "*ERRORS*\n" + "\n".join(
            [
                f"_{field.replace('_', '')}_    {self._escape(messages[0])}"
                for field, messages in serializer_errors.items()
            ]
        )

    async def _ask_for_new_attribute(self, update: Update, model_name: str, attribute: str, next_state: int) -> int:
        await self._reply(update, f"Type the {attribute} value for the new {model_name}")
        return next_state

    async def _create(
        self,
        update: Update,
        context: CallbackContext,
        serializer_class: Serializer,
        data: dict[str, Any],
        previous_state: int,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> tuple[int | None, Any | None]:
        chat = chat or await self._get_active_telegram_chat(update)
        if not chat or not update.effective_message:
            return ConversationHandler.END, None
        if (update.effective_message.text or "").lower() == "/cancel":
            return await Cancel()._execute_command(update, context), None
        instance, errors = await self._save_serializer_async(serializer_class(data=data))
        if not instance:
            next_state = previous_state
            logger.info(
                f"[TelegramBot] Attempt of {serializer_class.Meta.model.__name__.lower()} creation with invalid data",
                extra={"user": chat.user.id},
            )
            await self._reply(
                update,
                self._build_error_message_from_serializer_errors(errors),
            )
        else:
            logger.info(
                f"[TelegramBot] New {serializer_class.Meta.model.__name__.lower()} {instance.id} has been created",
                extra={"user": chat.user.id},
            )
        return next_state, instance

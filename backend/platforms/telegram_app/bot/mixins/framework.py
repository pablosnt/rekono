"""Base steps shared by all the bot conversations.

The conversations only differ in what they ask for, so asking, saving the answer,
and creating something with it are defined once here.
"""

from functools import cached_property
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
from projects.models import Project
from users.models import User


class BaseMixin(BaseTelegramBot):
    """Base step of a conversation, which knows how to move to the next one."""

    @cached_property
    def _mixin_states(self) -> list:
        """The steps of the conversation that this step belongs to."""
        return [] if not hasattr(self, "states_methods") else self.states_methods

    def _get_current_state(self, method: Callable) -> int:
        """Get the position of a step in the conversation.

        Args:
            method: Step whose position is searched.

        Returns:
            The position of the step, or the end of the conversation when this
            mixin doesn't declare any step.
        """
        return self._mixin_states.index(method) if len(self._mixin_states) > 0 else ConversationHandler.END

    def get_next_state(self, method: Callable) -> int:
        """Get the step that comes after another one.

        Args:
            method: Step whose next one is searched.

        Returns:
            The next step, or the end of the conversation if there is no next one.
        """
        current_state = self._get_current_state(method)
        return ConversationHandler.END if current_state == len(self._mixin_states) - 1 else current_state + 1

    def get_previous_state(self, method: Callable) -> int:
        """Get the step that comes before another one.

        Args:
            method: Step whose previous one is searched.

        Returns:
            The previous step, or the same one if it's the first of the
            conversation.
        """
        current_state = self._get_current_state(method)
        return current_state if current_state == 0 else current_state - 1

    async def go_to_next_state(
        self, update: Update, context: CallbackContext, next_state: int, invoke_next_state: bool = False
    ) -> int:
        """Move the conversation to its next step.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.
            next_state: Step to move to.
            invoke_next_state: Whether that step must be run right away, which the
              steps that only save an answer don't need.

        Returns:
            The step where the conversation is now.
        """
        if next_state != ConversationHandler.END and len(self._mixin_states) > 0:
            next_callable = self._mixin_states[next_state]
            # The steps that ask something or that answer something have to be run now,
            # otherwise the users would receive no message and the conversation would look stuck
            if (
                invoke_next_state
                or next_callable.__name__.startswith("ask_")
                or next_callable.__name__.startswith("reply_")
            ):
                return await next_callable(update, context)
        return next_state

    @sync_to_async
    def _is_queryset_async(self, queryset: QuerySet) -> bool:
        """Check if there is anything to choose from.

        Args:
            queryset: Options offered to the user, which are evaluated here.

        Returns:
            Whether the queryset holds at least one option.
        """
        return bool(queryset)

    @sync_to_async
    def queryset_exists_async(self, queryset: QuerySet) -> bool:
        """Check if there is anything that matches a query.

        Args:
            queryset: Query to be checked, which isn't evaluated.

        Returns:
            Whether the query matches at least one object.
        """
        return queryset.exists()

    @sync_to_async
    def _get_model_instance_async(self, model: Any, pk: int, user: User) -> Any:
        """Get what a user chose, if they are allowed to choose it.

        Args:
            model: Kind of thing that was chosen.
            pk: Identifier that the user answered with.
            user: User that answered.

        Returns:
            The chosen thing, or None if it doesn't exist or belongs to a project
            that the user isn't a member of, since the identifier comes from a
            button that the users can answer with any value.
        """
        members_field = None
        if model == Project:
            members_field = "members"
        elif model._project_field:
            members_field = f"{model._project_field}__members"
        return (
            model.objects.filter(**{members_field: user, "pk": pk}).first()
            if members_field
            else model.objects.get(pk=pk)
        )

    @sync_to_async
    def _get_keyboard_from_queryset_async(self, queryset: QuerySet, attribute: str) -> list[InlineKeyboardButton]:
        """Get one button per thing that the users can choose from.

        Args:
            queryset: Things that the users can choose from.
            attribute: Field that each button is named after.

        Returns:
            The buttons, sorted by their name, and each one carrying the
            identifier of what it represents.
        """
        return [InlineKeyboardButton(getattr(i, attribute), callback_data=i.id) for i in queryset.order_by(attribute)]

    def _get_inline_keyboard_markup(
        self, keyboard: list[InlineKeyboardButton], options_per_row: int
    ) -> InlineKeyboardMarkup:
        """Arrange the buttons of a question in rows.

        Args:
            keyboard: Buttons to arrange.
            options_per_row: Buttons that each row can have, which depends on how
              long their names are.

        Returns:
            The buttons as Telegram shows them.
        """
        return InlineKeyboardMarkup(
            [keyboard[item : item + options_per_row] for item in range(0, len(keyboard), options_per_row)]
        )

    @sync_to_async
    def _save_serializer_async(self, serializer: Serializer) -> tuple[Any | None, dict[str, Any]]:
        """Create something with the data that the users provided.

        Args:
            serializer: Serializer with the data to create the thing with.

        Returns:
            The created thing, or the errors that stopped it from being created.
        """
        try:
            return (serializer.save(), {}) if serializer.is_valid() else (None, serializer.errors)
        except IntegrityError:
            return None, {serializer.Meta.model.__name__.lower(): ["This entity already exists in the database"]}

    def _build_error_message_from_serializer_errors(self, serializer_errors: dict[str, Any]) -> str:
        """Write the errors that stopped something from being created.

        Args:
            serializer_errors: Errors of each field, as the serializer reports them.

        Returns:
            One line per field, escaped so Telegram doesn't read it as Markdown.
        """
        return "*ERRORS*\n" + "\n".join(
            [
                f"_{field.replace('_', '')}_    {self.escape(messages[0])}"
                for field, messages in serializer_errors.items()
            ]
        )

    async def ask(
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
        """Ask the users to choose one of the things that they can choose from.

        Args:
            update: Message that the user wrote.
            queryset: Things that the users can choose from.
            attribute: Field that each button is named after.
            options_per_row: Buttons that each row can have.
            message: Question to ask.
            not_found_message: Answer when there is nothing to choose from.
            next_state: Step that saves the answer.
            chat: Chat that is running the command, if the caller already knows it.

        Returns:
            The step that saves the answer, or the end of the conversation if the
            chat can't run the command or if there is nothing to choose from.
        """
        chat = chat or await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        if not await self._is_queryset_async(queryset):
            await self.reply(update, not_found_message)
            return ConversationHandler.END
        keyboard = await self._get_keyboard_from_queryset_async(queryset, attribute)
        await self.reply(update, message, reply_markup=self._get_inline_keyboard_markup(keyboard, options_per_row))
        return next_state

    async def ask_values(
        self,
        update: Update,
        values: list[str],
        options_per_row: int,
        message: str,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        """Ask the users to choose one of some fixed values.

        Args:
            update: Message that the user wrote.
            values: Values that the users can choose from.
            options_per_row: Buttons that each row can have.
            message: Question to ask.
            next_state: Step that saves the answer.
            chat: Chat that is running the command, if the caller already knows it.

        Returns:
            The step that saves the answer, or the end of the conversation if the
            chat can't run the command.
        """
        chat = chat or await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        keyboard = [InlineKeyboardButton(v.capitalize(), callback_data=v) for v in values]
        await self.reply(update, message, reply_markup=self._get_inline_keyboard_markup(keyboard, options_per_row))
        return next_state

    async def save(
        self,
        update: Update,
        context: CallbackContext,
        context_key: Context,
        model: Any,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        """Remember what the users chose.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.
            context_key: Kind of data that was chosen.
            model: Kind of thing that was chosen.
            next_state: Step that comes after this one.
            chat: Chat that is running the command, if the caller already knows it.

        Returns:
            The next step, or the end of the conversation if the chat can't run the
            command or if the users answered with nothing.
        """
        chat = chat or await self.get_active_telegram_chat(update)
        if chat and update.callback_query and update.callback_query.data:
            entity = await self._get_model_instance_async(model, int(update.callback_query.data), chat.user)
            self.add_context_value(context, context_key, entity)
            await update.callback_query.answer(f"{model.__name__} #{update.callback_query.data} has been selected")
            return next_state
        elif update.callback_query:
            await update.callback_query.answer()
        return ConversationHandler.END

    async def save_value(
        self,
        update: Update,
        context: CallbackContext,
        context_key: Context,
        name: str,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> int:
        """Remember which value the users chose.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.
            context_key: Kind of data that was chosen.
            name: Name of what was chosen, used to confirm it to the users.
            next_state: Step that comes after this one.
            chat: Chat that is running the command, if the caller already knows it.

        Returns:
            The next step, or the end of the conversation if the chat can't run the
            command or if the users answered with nothing.
        """
        chat = chat or await self.get_active_telegram_chat(update)
        if chat and update.callback_query and update.callback_query.data:
            self.add_context_value(context, context_key, update.callback_query.data)
            await update.callback_query.answer(f"{name} {update.callback_query.data} has been selected")
            return next_state
        elif update.callback_query:
            await update.callback_query.answer()
        return ConversationHandler.END

    async def ask_for_new_attribute(self, update: Update, model_name: str, attribute: str, next_state: int) -> int:
        """Ask the users to write the value of a field.

        Args:
            update: Message that the user wrote.
            model_name: Name of what is being created.
            attribute: Field whose value is asked for.
            next_state: Step that creates the thing with that value.

        Returns:
            The step that creates the thing.
        """
        await self.reply(update, f"Type the {attribute} value for the new {model_name}")
        return next_state

    async def create(
        self,
        update: Update,
        context: CallbackContext,
        serializer_class: Serializer,
        data: dict[str, Any],
        previous_state: int,
        next_state: int,
        chat: TelegramChat | None = None,
    ) -> tuple[int | None, Any | None]:
        """Create something with the data that the users wrote.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.
            serializer_class: Serializer that validates and creates the thing.
            data: Data to create the thing with.
            previous_state: Step to go back to if the data isn't valid.
            next_state: Step that comes after creating the thing.
            chat: Chat that is running the command, if the caller already knows it.

        Returns:
            The next step and the created thing, or the previous step and nothing
            if the data isn't valid, so the users can write it again.
        """
        chat = chat or await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END, None
        # The state's MessageHandler(filters.TEXT, ...) matches "/cancel" as plain text too, so it
        # never reaches the ConversationHandler's Cancel fallback; it has to be handled here instead
        if (update.effective_message.text or "").lower() == "/cancel":
            return await Cancel().execute_command(update, context), None
        instance, errors = await self._save_serializer_async(serializer_class(data=data))
        if not instance:
            next_state = previous_state
            self.logger.info(
                f"[TelegramBot] Attempt to create {serializer_class.Meta.model.__name__.lower()} with invalid data",
                extra={"user": chat.user.id},
            )
            await self.reply(update, self._build_error_message_from_serializer_errors(errors))
        else:
            self.logger.info(
                f"[TelegramBot] New {serializer_class.Meta.model.__name__.lower()} #{instance.id} has been created",
                extra={"user": chat.user.id},
            )
        return next_state, instance

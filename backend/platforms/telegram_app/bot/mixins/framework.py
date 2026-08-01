"""Framework mixins for Telegram Bot conversations and CRUD operations.

Provides base mixins for conversation state management, pagination,
CRUD operations, and interactive keyboard handling in Telegram Bot workflows.
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
    """Base mixin for Telegram Bot conversation state management.

    Provides utilities for managing conversation states, navigation between
    states, and handling conversation flow control in complex workflows.
    """

    @cached_property
    def _mixin_states(self) -> list:
        """Get the list of conversation state methods.

        Returns:
            list: List of state methods or empty list if not defined.
        """
        return [] if not hasattr(self, "states_methods") else self.states_methods

    def _get_current_state(self, method: Callable) -> int:
        """Get the current state index for a method.

        Args:
            method (Callable): The method to find in the states list.

        Returns:
            int: The state index or ConversationHandler.END if not found.
        """
        return self._mixin_states.index(method) if len(self._mixin_states) > 0 else ConversationHandler.END

    def get_next_state(self, method: Callable) -> int:
        """Get the next state in the conversation flow.

        Args:
            method (Callable): The current method to find next state for.

        Returns:
            int: The next state index or ConversationHandler.END if at the end.
        """
        current_state = self._get_current_state(method)
        return ConversationHandler.END if current_state == len(self._mixin_states) - 1 else current_state + 1

    def get_previous_state(self, method: Callable) -> int:
        """Get the previous state in the conversation flow.

        Args:
            method (Callable): The current method to find previous state for.

        Returns:
            int: The previous state index or 0 if at the beginning.
        """
        current_state = self._get_current_state(method)
        return current_state if current_state == 0 else current_state - 1

    async def go_to_next_state(
        self, update: Update, context: CallbackContext, next_state: int, invoke_next_state: bool = False
    ) -> int:
        """Navigate to the next state in the conversation flow.

        Automatically executes certain state methods based on naming conventions
        or explicit invocation. Methods starting with 'ask_' or 'reply_' are
        automatically executed, or if invoke_next_state is True.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.
            next_state (int): The next state index to navigate to.
            invoke_next_state (bool): Force execution of next state method.

        Returns:
            int: State index or result of state method execution.
        """
        if next_state != ConversationHandler.END and len(self._mixin_states) > 0:
            next_callable = self._mixin_states[next_state]
            if (
                invoke_next_state
                or next_callable.__name__.startswith("ask_")
                or next_callable.__name__.startswith("reply_")
            ):
                return await next_callable(update, context)
        return next_state

    @sync_to_async
    def _is_queryset_async(self, queryset: QuerySet) -> bool:
        """Check if queryset has any results (async wrapper).

        Args:
            queryset (QuerySet): Django QuerySet to check.

        Returns:
            bool: True if queryset contains any objects.
        """
        return bool(queryset)

    @sync_to_async
    def queryset_exists_async(self, queryset: QuerySet) -> bool:
        """Check if queryset exists using Django's exists() method (async wrapper).

        Args:
            queryset (QuerySet): Django QuerySet to check for existence.

        Returns:
            bool: True if queryset has any matching records.
        """
        return queryset.exists()

    @sync_to_async
    def _get_model_instance_async(self, model: Any, pk: int, user: User) -> Any:
        """Get model instance by primary key, limited to the user's projects (async wrapper).

        The primary key comes from the callback data of a Telegram button, which the
        user can replay with any value, so the lookup is scoped to the projects the
        user belongs to. The project relation is taken from the model's
        _project_field, except for Project itself, which exposes its members
        directly. Models without a project relation are global and are retrieved
        without any scoping.

        Args:
            model (Any): Django model class to query.
            pk (int): Primary key of the instance to retrieve.
            user (User): User that must be a member of the related project.

        Returns:
            Any: Model instance matching the primary key, or None if it doesn't
                 exist or belongs to a project the user isn't a member of.
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
        """Generate inline keyboard buttons from QuerySet (async wrapper).

        Args:
            queryset (QuerySet): Django QuerySet to convert to buttons.
            attribute (str): Model attribute to use as button text.

        Returns:
            list[InlineKeyboardButton]: List of inline keyboard buttons.
        """
        return [InlineKeyboardButton(getattr(i, attribute), callback_data=i.id) for i in queryset.order_by(attribute)]

    def _get_inline_keyboard_markup(
        self, keyboard: list[InlineKeyboardButton], options_per_row: int
    ) -> InlineKeyboardMarkup:
        """Create inline keyboard markup with specified buttons per row.

        Args:
            keyboard (list[InlineKeyboardButton]): List of keyboard buttons.
            options_per_row (int): Number of buttons to display per row.

        Returns:
            InlineKeyboardMarkup: Formatted keyboard markup for Telegram.
        """
        return InlineKeyboardMarkup(
            [keyboard[item : item + options_per_row] for item in range(0, len(keyboard), options_per_row)]
        )

    @sync_to_async
    def _save_serializer_async(self, serializer: Serializer) -> tuple[Any | None, dict[str, Any]]:
        """Save serializer data with validation and integrity error handling (async wrapper).

        Args:
            serializer (Serializer): The serializer to validate and save.

        Returns:
            tuple[Any | None, dict[str, Any]]: Tuple of (saved_instance, errors_dict).
                                              Returns (instance, {}) on success,
                                              (None, validation_errors) on validation failure,
                                              or (None, integrity_error) on database conflicts.
        """
        try:
            return (serializer.save(), {}) if serializer.is_valid() else (None, serializer.errors)
        except IntegrityError:
            return None, {serializer.Meta.model.__name__.lower(): ["This entity already exists in the database"]}

    def _build_error_message_from_serializer_errors(self, serializer_errors: dict[str, Any]) -> str:
        """Build formatted error message from serializer validation errors.

        Args:
            serializer_errors (dict[str, Any]): Dictionary of field validation errors.

        Returns:
            str: Formatted error message for Telegram display.
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
        """Display selection options from a QuerySet with inline keyboard.

        Creates an inline keyboard from QuerySet objects and displays selection
        options to the user with pagination support.

        Args:
            update (Update): The Telegram update containing user interaction.
            queryset (QuerySet): Django QuerySet containing selectable objects.
            attribute (str): Model attribute to use as display text.
            options_per_row (int): Number of buttons to display per row.
            message (str): Message to display with the selection options.
            not_found_message (str): Message to display when no options available.
            next_state (int): Next conversation state after selection.
            chat (TelegramChat, optional): Chat context. Auto-retrieved if None.

        Returns:
            int: Next conversation state or ConversationHandler.END.
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
        """Display selection options from a list of string values.

        Creates an inline keyboard from string values and displays selection
        options to the user with pagination support.

        Args:
            update (Update): The Telegram update containing user interaction.
            values (list[str]): List of string values for selection.
            options_per_row (int): Number of buttons to display per row.
            message (str): Message to display with the selection options.
            next_state (int): Next conversation state after selection.
            chat (TelegramChat, optional): Chat context. Auto-retrieved if None.

        Returns:
            int: Next conversation state or ConversationHandler.END.
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
        """Save selected model instance to conversation context.

        Processes user's callback query selection, retrieves the model instance,
        and stores it in the conversation context for subsequent use. The instance
        is looked up on behalf of the chat user, so only entities from the user's
        projects can be selected.

        Args:
            update (Update): The Telegram update containing callback query.
            context (CallbackContext): The callback context for the conversation.
            context_key (Context): Context key for storing the selected instance.
            model (Any): Django model class for the selected instance.
            next_state (int): Next conversation state after saving.
            chat (TelegramChat, optional): Chat context. Auto-retrieved if None.

        Returns:
            int: Next conversation state or ConversationHandler.END.
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
        """Save selected string value to conversation context.

        Processes user's callback query selection and stores the string value
        in the conversation context for subsequent use.

        Args:
            update (Update): The Telegram update containing callback query.
            context (CallbackContext): The callback context for the conversation.
            context_key (Context): Context key for storing the selected value.
            name (str): Display name for the selected value type.
            next_state (int): Next conversation state after saving.
            chat (TelegramChat, optional): Chat context. Auto-retrieved if None.

        Returns:
            int: Next conversation state or ConversationHandler.END.
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
        """Prompt user to input a new attribute value for model creation.

        Args:
            update (Update): The Telegram update containing user interaction.
            model_name (str): Name of the model being created.
            attribute (str): Name of the attribute to input.
            next_state (int): Next conversation state after input.

        Returns:
            int: Next conversation state for text input processing.
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
        """Create a new model instance using serializer validation.

        Validates user input data and creates a new model instance with proper
        error handling and logging. Supports cancel command during creation.

        Args:
            update (Update): The Telegram update containing user input.
            context (CallbackContext): The callback context for the conversation.
            serializer_class (Serializer): Django serializer class for validation.
            data (dict[str, Any]): Data dictionary for model creation.
            previous_state (int): State to return to on validation error.
            next_state (int): State to proceed to on successful creation.
            chat (TelegramChat, optional): Chat context. Auto-retrieved if None.

        Returns:
            tuple[int | None, Any | None]: Next state and created instance.
                                         Instance is None if creation failed.
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

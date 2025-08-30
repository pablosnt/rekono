"""Telegram Bot mixins for input parameter management in security workflows.

Provides input parameter selection and creation functionality for technology
and vulnerability parameters used in security testing configurations.
"""

from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from input_types.enums import InputTypeName
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import InputTechnologySerializer, InputVulnerabilitySerializer
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.models import Input
from users.models import User


class InputMixin(BaseMixin):
    """Base mixin for input parameter management.

    Provides common functionality for input parameter selection and creation
    including keyboard generation for existing parameters.

    Attributes:
        model (Model): Django model class for input parameters (default: InputTechnology).
    """

    model = InputTechnology

    @sync_to_async
    def _get_keyboard_async(self, user: User) -> list[InlineKeyboardButton]:
        """Generate keyboard buttons for user's existing input parameters (async wrapper).

        Args:
            user (User): User to filter parameters for.

        Returns:
            list[InlineKeyboardButton]: Buttons for existing parameters plus "New one" option.
        """
        return [
            InlineKeyboardButton(" - ".join([v for v in i.parse().values() if v]), callback_data=i.id)
            for i in self.model.objects.filter(tasks__target__project__members=user).all()
        ] + [InlineKeyboardButton("New one", callback_data=None)]


class InputTechnologyMixin(InputMixin):
    """Mixin for managing technology input parameters.

    Provides functionality for selecting and creating technology-specific
    input parameters for security tool configuration.

    Attributes:
        model (Model): InputTechnology model class for technology parameters.
    """

    model = InputTechnology

    async def ask_for_input_technology(self, update: Update, context: CallbackContext) -> int:
        """Display technology input parameter selection options.

        Shows existing technology parameters or option to create new ones
        for security tool configuration.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state or ConversationHandler.END.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        tool = self.get_context_value(context, Context.TOOL)
        if not tool:
            self.reply(update, "No tool selected")
            return ConversationHandler.END
        if not await self.queryset_exists_async(
            Input.objects.filter(argument__tool=tool, type__name=InputTypeName.TECHNOLOGY)
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.create_input_technology))
        if not await self.queryset_exists_async(
            InputTechnology.objects.filter(tasks__target__project__members=chat.user).exists()
        ):
            return await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input technology", "'name \- version'", self.get_next_state(self.save_input_technology)
                ),
            )
        keyboard = await self._get_keyboard_async(chat.user)
        await self.reply(
            update,
            "Choose technology to use as input parameter",
            reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]),
        )
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_input_technology))

    async def save_input_technology(self, update: Update, context: CallbackContext) -> int:
        """Save selected technology parameter to conversation context.

        Processes technology parameter selection or prompts for new parameter
        creation based on user choice.

        Args:
            update (Update): The Telegram update containing callback selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for parameter creation or selection.
        """
        self.validate_update(update)
        return (
            await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input technology", "'name \- version'", self.get_next_state(self.save_input_technology)
                ),
            )
            if not update.callback_query or not update.callback_query.data
            else await self.go_to_next_state(
                update,
                context,
                await self.save(
                    update,
                    context,
                    Context.INPUT_TECHNOLOGY,
                    InputTechnology,
                    self.get_next_state(self.create_input_technology),
                ),
            )
        )

    async def create_input_technology(self, update: Update, context: CallbackContext) -> int:
        """Create new technology input parameter from user input.

        Processes user input to create technology parameter with name and optional
        version for use in security testing workflows.

        Args:
            update (Update): The Telegram update containing technology input.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after parameter creation.
        """
        self.validate_update(update)
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        name = update.effective_message.text
        version = None
        if name and " - " in name:
            name, version = name.split(" - ", 1)
        next_state, instance = await self._create(
            update,
            context,
            InputTechnologySerializer,
            {"name": name, "version": version},
            self.get_previous_state(self.create_input_technology),
            self.get_next_state(self.create_input_technology),
        )
        if instance:
            await self.reply(update, f"New input technology *{self.escape(instance.name)}* has been created")
            self.add_context_value(context, Context.INPUT_TECHNOLOGY, instance)
        return await self.go_to_next_state(update, context, next_state)


class InputVulnerabilityMixin(InputMixin):
    """Mixin for managing vulnerability input parameters.

    Provides functionality for selecting and creating vulnerability-specific
    input parameters for security tool configuration.

    Attributes:
        model (Model): InputVulnerability model class for vulnerability parameters.
    """

    model = InputVulnerability

    async def ask_for_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        """Display vulnerability input parameter selection options.

        Shows existing vulnerability parameters or option to create new ones
        for security tool configuration.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state or ConversationHandler.END.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        tool = self.get_context_value(context, Context.TOOL)
        if not tool:
            self.reply(update, "No tool selected")
            return ConversationHandler.END
        if not await self.queryset_exists_async(
            Input.objects.filter(argument__tool=tool, type__name=InputTypeName.VULNERABILITY)
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.create_input_vulnerability))
        if not await self.queryset_exists_async(
            InputVulnerability.objects.filter(tasks__target__project__members=chat.user).exists()
        ):
            return await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input vulnerability", "cve", self.get_next_state(self.save_input_vulnerability)
                ),
            )
        keyboard = await self._get_keyboard_async(chat.user)
        await self.reply(
            update,
            "Choose vulnerability to use as input parameter",
            reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]),
        )
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_input_vulnerability))

    async def save_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        """Save selected vulnerability parameter to conversation context.

        Processes vulnerability parameter selection or prompts for new parameter
        creation based on user choice.

        Args:
            update (Update): The Telegram update containing callback selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for parameter creation or selection.
        """
        self.validate_update(update)
        return (
            await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input vulnerability", "cve", self.get_next_state(self.ask_for_input_vulnerability)
                ),
            )
            if not update.callback_query or not update.callback_query.data
            else await self.go_to_next_state(
                update,
                context,
                await self.save(
                    update,
                    context,
                    Context.INPUT_VULNERABILITY,
                    InputVulnerability,
                    self.get_next_state(self.create_input_vulnerability),
                ),
            )
        )

    async def create_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        """Create new vulnerability input parameter from user input.

        Processes user input to create vulnerability parameter with CVE identifier
        for use in security testing workflows.

        Args:
            update (Update): The Telegram update containing vulnerability input.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after parameter creation.
        """
        self.validate_update(update)
        next_state, instance = await self.create(
            update,
            context,
            InputVulnerabilitySerializer,
            {"cve": update.effective_message.text if update.effective_message else None},
            self.get_previous_state(self.create_input_vulnerability),
            self.get_next_state(self.create_input_vulnerability),
        )
        if instance:
            await self.reply(update, f"New input vulnerability *{self.escape(instance.cve)}* has been created")
            self.add_context_value(context, Context.INPUT_VULNERABILITY, instance)
        return await self.go_to_next_state(update, context, next_state)

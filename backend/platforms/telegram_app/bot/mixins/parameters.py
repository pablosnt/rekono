"""Steps that ask for the data that the users provide as input for a tool.

The questions are only asked if the chosen configuration accepts that kind of data,
and the users can reuse what they provided before instead of writing it again.
"""

from typing import Any

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
    """Base steps that choose the data that the users provide for a tool."""

    @sync_to_async
    def _get_keyboard_async(self, user: User, model: Any) -> list[InlineKeyboardButton]:
        """Get one button per parameter that a user can reuse, plus a new one.

        Args:
            user: User that will answer.
            model: Kind of parameter to offer.

        Returns:
            The parameters used by the tasks of the projects that the user belongs
            to, since the parameters aren't tied to any project.
        """
        return [
            InlineKeyboardButton(
                " - ".join([value for value in item.parse(None).values() if value]), callback_data=item.id
            )
            for item in model.objects.filter(tasks__target__project__members=user).all().distinct()
        ] + [InlineKeyboardButton("New one", callback_data=0)]


class InputTechnologyMixin(InputMixin):
    """Steps that choose the technology that the users provide for a tool."""

    async def ask_for_input_technology(self, update: Update, context: CallbackContext) -> int:
        """Ask the users for a technology, if the configuration accepts one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, the step after creating a technology if
            the configuration doesn't accept one, the step that creates it if there
            is nothing to reuse, or the end of the conversation if the chat can't
            run the command or if no configuration was chosen.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        configuration = self.get_context_value(context, Context.CONFIGURATION)
        if not configuration:
            await self.reply(update, "No configuration selected")
            return ConversationHandler.END
        if not await self.queryset_exists_async(
            Input.objects.filter(argument__configuration=configuration, type__name=InputTypeName.TECHNOLOGY)
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.create_input_technology))
        if not await self.queryset_exists_async(
            InputTechnology.objects.filter(tasks__target__project__members=chat.user)
        ):
            return await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input technology", "'name \- version'", self.get_next_state(self.save_input_technology)
                ),
            )
        await self.reply(
            update,
            "Choose technology to use as input parameter",
            reply_markup=InlineKeyboardMarkup(
                [[item] for item in await self._get_keyboard_async(chat.user, InputTechnology)]
            ),
        )
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_input_technology))

    async def save_input_technology(self, update: Update, context: CallbackContext) -> int:
        """Remember the technology that the users chose, or ask for a new one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step after creating a technology, or the step that creates it if
            the users chose to provide a new one.
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
            if not update.callback_query or not update.callback_query.data or update.callback_query.data == "0"
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
        """Create the technology that the users wrote.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step, or the previous one if what the users wrote isn't valid.
        """
        self.validate_update(update)
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        # The name and the version are written in the same message, separated by a dash, so the
        # users only have to answer once
        name = update.effective_message.text
        version = None
        if name and " - " in name:
            name, version = name.split(" - ", 1)
        next_state, instance = await self.create(
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
        return await self.go_to_next_state(update, context, next_state, invoke_next_state=instance is None)


class InputVulnerabilityMixin(InputMixin):
    """Steps that choose the vulnerability that the users provide for a tool."""

    async def ask_for_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        """Ask the users for a vulnerability, if the configuration accepts one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, the step after creating a vulnerability
            if the configuration doesn't accept one, the step that creates it if
            there is nothing to reuse, or the end of the conversation if the chat
            can't run the command or if no configuration was chosen.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        configuration = self.get_context_value(context, Context.CONFIGURATION)
        if not configuration:
            await self.reply(update, "No configuration selected")
            return ConversationHandler.END
        if not await self.queryset_exists_async(
            Input.objects.filter(argument__configuration=configuration, type__name=InputTypeName.VULNERABILITY)
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.create_input_vulnerability))
        if not await self.queryset_exists_async(
            InputVulnerability.objects.filter(tasks__target__project__members=chat.user)
        ):
            return await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input vulnerability", "cve", self.get_next_state(self.save_input_vulnerability)
                ),
            )
        await self.reply(
            update,
            "Choose vulnerability to use as input parameter",
            reply_markup=InlineKeyboardMarkup(
                [[item] for item in await self._get_keyboard_async(chat.user, InputVulnerability)]
            ),
        )
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_input_vulnerability))

    async def save_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        """Remember the vulnerability that the users chose, or ask for a new one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step after creating a vulnerability, or the step that creates it if
            the users chose to provide a new one.
        """
        self.validate_update(update)
        return (
            await self.go_to_next_state(
                update,
                context,
                await self.ask_for_new_attribute(
                    update, "input vulnerability", "cve", self.get_next_state(self.save_input_vulnerability)
                ),
            )
            if not update.callback_query or not update.callback_query.data or update.callback_query.data == "0"
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
        """Create the vulnerability that the users wrote.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step, or the previous one if what the users wrote isn't a
            valid CVE identifier.
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
        return await self.go_to_next_state(update, context, next_state, invoke_next_state=instance is None)

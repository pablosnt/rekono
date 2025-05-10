from asgiref.sync import sync_to_async
from input_types.enums import InputTypeName
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler
from tools.models import Input
from users.models import User


class InputMixin(BaseMixin):
    model = InputTechnology

    @sync_to_async
    def _get_keyboard_async(self, user: User) -> list[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(" - ".join([v for v in i.parse().values() if v]), callback_data=i.id)
            for i in self.model.objects.filter(tasks__target__project__members=user).all()
        ] + [InlineKeyboardButton("Define one", callback_data=None)]


class InputTechnologyMixin(InputMixin):
    model = InputTechnology

    async def _ask_for_input_technology(self, update: Update, context: CallbackContext) -> int:
        chat = await self._get_active_telegram_chat(update)
        tool = self._get_context_value(context, Context.TOOL)
        if not chat or not tool:
            return ConversationHandler.END
        if not await self._queryset_exists_async(
            Input.objects.filter(argument__tool=tool, type__name=InputTypeName.TECHNOLOGY)
        ):
            return await self._go_to_next_state(update, context, self._get_next_state(self._create_input_technology))
        if not await self._queryset_exists_async(
            InputTechnology.objects.filter(tasks__target__project__members=chat.user).exists()
        ):
            return await self._go_to_next_state(
                update,
                context,
                await self._ask_for_new_attribute(
                    update,
                    "input technology",
                    "'name \- version'",
                    self._get_next_state(self._save_input_technology),
                ),
            )
        keyboard = await self._get_keyboard_async(chat.user)
        await self._reply(
            update,
            "Choose technology to use as input parameter",
            reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]),
        )
        return await self._go_to_next_state(update, context, self._get_next_state(self._ask_for_input_technology))

    async def _save_input_technology(self, update: Update, context: CallbackContext) -> int:
        return (
            await self._go_to_next_state(
                update,
                context,
                await self._ask_for_new_attribute(
                    update,
                    "input technology",
                    "'name \- version'",
                    self._get_next_state(self._save_input_technology),
                ),
            )
            if not update.callback_query or not update.callback_query.data
            else await self._go_to_next_state(
                update,
                context,
                await self._save(
                    update,
                    context,
                    Context.INPUT_TECHNOLOGY,
                    InputTechnology,
                    self._get_next_state(self._create_input_technology),
                ),
            )
        )

    async def _create_input_technology(self, update: Update, context: CallbackContext) -> int:
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
            {
                "name": name,
                "version": version,
            },
            self._get_previous_state(self._create_input_technology),
            self._get_next_state(self._create_input_technology),
        )
        if instance:
            await self._reply(
                update,
                f"New input technology *{self._escape(instance.name)}* has been created",
            )
        return await self._go_to_next_state(update, context, next_state)


class InputVulnerabilityMixin(InputMixin):
    model = InputVulnerability

    async def _ask_for_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        chat = await self._get_active_telegram_chat(update)
        tool = self._get_context_value(context, Context.TOOL)
        if not chat or not tool:
            return ConversationHandler.END
        if not await self._queryset_exists_async(
            Input.objects.filter(argument__tool=tool, type__name=InputTypeName.VULNERABILITY)
        ):
            return await self._go_to_next_state(update, context, self._get_next_state(self._create_input_vulnerability))
        if not await self._queryset_exists_async(
            InputVulnerability.objects.filter(tasks__target__project__members=chat.user).exists()
        ):
            return await self._go_to_next_state(
                update,
                context,
                await self._ask_for_new_attribute(
                    update,
                    "input vulnerability",
                    "cve",
                    self._get_next_state(self._save_input_vulnerability),
                ),
            )
        keyboard = await self._get_keyboard_async(chat.user)
        await self._reply(
            update,
            "Choose vulnerability to use as input parameter",
            reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]),
        )
        return await self._go_to_next_state(update, context, self._get_next_state(self._ask_for_input_vulnerability))

    async def _save_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        return (
            await self._go_to_next_state(
                update,
                context,
                await self._ask_for_new_attribute(
                    update,
                    "input vulnerability",
                    "cve",
                    self._get_next_state(self._ask_for_input_vulnerability),
                ),
            )
            if not update.callback_query or not update.callback_query.data
            else await self._go_to_next_state(
                update,
                context,
                await self._save(
                    update,
                    context,
                    Context.INPUT_VULNERABILITY,
                    InputVulnerability,
                    self._get_next_state(self._create_input_vulnerability),
                ),
            )
        )

    async def _create_input_vulnerability(self, update: Update, context: CallbackContext) -> int:
        next_state, instance = await self._create(
            update,
            context,
            InputVulnerabilitySerializer,
            {
                "cve": (update.effective_message.text if update.effective_message else None),
            },
            self._get_previous_state(self._create_input_vulnerability),
            self._get_next_state(self._create_input_vulnerability),
        )
        if instance:
            await self._reply(
                update,
                f"New input vulnerability *{self._escape(instance.cve)}* has been created",
            )
        return await self._go_to_next_state(update, context, next_state)

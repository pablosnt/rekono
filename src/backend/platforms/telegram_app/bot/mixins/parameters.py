from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


class InputTechnologyMixin(BaseMixin):
    async def _ask_for_new_technology(
        self, update: Update, context: CallbackContext
    ) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_for_new_attribute(
                update,
                "input technology",
                "'name \- version'",
                self._get_next_state(self._ask_for_new_technology),
            ),
        )

    async def _create_input_technology(
        self, update: Update, context: CallbackContext
    ) -> int:
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        name = update.effective_message.text
        version = None
        if name and " - " in name:
            name, version = name.split(" - ", 1)
        target = self._get_context_value(context, Context.TARGET)
        next_state, instance = await self._create(
            update,
            context,
            InputTechnologySerializer,
            {
                "target": target.id if target else None,
                "name": name,
                "version": version,
            },
            self._get_previous_state(self._create_input_technology),
            self._get_next_state(self._create_input_technology),
        )
        if instance:
            await self._reply(
                update,
                f"New input technology *{self._escape(instance.name)}* has been created in target *{self._escape(instance.target.target)}*",
            )
        self._remove_all_context_values(context)
        return await self._go_to_next_state(update, context, next_state)


class InputVulnerabilityMixin(BaseMixin):
    async def _ask_for_new_vulnerability(
        self, update: Update, context: CallbackContext
    ) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_for_new_attribute(
                update,
                "input vulnerability",
                "cve",
                self._get_next_state(self._ask_for_new_vulnerability),
            ),
        )

    async def _create_input_vulnerability(
        self, update: Update, context: CallbackContext
    ) -> int:
        target = self._get_context_value(context, Context.TARGET)
        next_state, instance = await self._create(
            update,
            context,
            InputVulnerabilitySerializer,
            {
                "target": target.id if target else None,
                "cve": update.effective_message.text,
            },
            self._get_previous_state(self._create_input_vulnerability),
            self._get_next_state(self._create_input_vulnerability),
        )
        if instance:
            await self._reply(
                update,
                f"New input vulnerability *{self._escape(instance.cve)}* has been created in target *{self._escape(instance.target.target)}*",
            )
        self._remove_all_context_values(context)
        return await self._go_to_next_state(update, context, next_state)

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from target_ports.serializers import TargetPortSerializer
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


class TargetPortMixin(BaseMixin):
    async def _ask_for_new_target_port(
        self, update: Update, context: CallbackContext
    ) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_for_new_attribute(
                update,
                "target port",
                "port",
                self._get_next_state(self._ask_for_new_target_port),
            ),
        )

    async def _create_target_port(
        self, update: Update, context: CallbackContext
    ) -> int:
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        if update.effective_message.text.lower() == "/cancel":
            return await Cancel()._execute_command(update, context)
        try:
            port = int(update.effective_message.text)
        except ValueError:
            self._reply(update, "Port must be a valid number")
            return await self._go_to_next_state(
                update, context, self._get_previous_state(self._create_target_port)
            )
        target = self._get_context_value(context, Context.TARGET)
        authentication = self._get_context_value(context, Context.AUTHENTICATION)
        data = {
            "target": target.id if target else None,
            "port": port,
            "path": None,
        }
        if authentication:
            data["authentication"] = authentication.id
        next_state, instance = await self._create(
            update,
            context,
            TargetPortSerializer,
            data,
            self._get_previous_state(self._create_target_port),
            self._get_next_state(self._create_target_port),
        )
        if instance:
            await self._reply(
                update,
                f"New target port *{instance.port}* has been created in target *{self._escape(instance.target.target)}*",
            )
        self._remove_all_context_values(context)
        return await self._go_to_next_state(update, context, next_state)
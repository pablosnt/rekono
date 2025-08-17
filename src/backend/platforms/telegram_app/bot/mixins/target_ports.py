from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from target_ports.serializers import TargetPortSerializer


class TargetPortMixin(BaseMixin):
    async def ask_for_new_target_port(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_for_new_attribute(
                update, "target port", "port", self.get_next_state(self.ask_for_new_target_port), ç
            ),
        )

    async def create_target_port(self, update: Update, context: CallbackContext) -> int | None:
        self.validate_update(update)
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        if update.effective_message.text.lower() == "/cancel":
            return await Cancel().execute_command(update, context)
        try:
            port = int(update.effective_message.text)
        except ValueError:
            self.reply(update, "Port must be a valid number")
            return await self.go_to_next_state(update, context, self.get_previous_state(self.create_target_port))
        target = self.get_context_value(context, Context.TARGET)
        if not target:
            self.reply(update, "No target selected")
            return ConversationHandler.END
        next_state, instance = await self.create(
            update,
            context,
            TargetPortSerializer,
            {"target": target.id, "port": port, "path": None},
            self.get_previous_state(self.create_target_port),
            self.get_next_state(self.create_target_port),
        )
        if instance:
            self.add_context_value(context, Context.TARGET_PORT, instance)
        return await self.go_to_next_state(update, context, next_state)

    async def reply_summary(self, update: Update, context: Context) -> int:
        self.validate_update(update)
        target_port = self.get_context_value(context, Context.TARGET_PORT)
        if target_port:
            await self.reply(
                update,
                f"New target port *{target_port.port}* has been created in target *{self.escape(target_port.target.target)}*",
            )
        self.remove_all_context_values(context)
        return await self.go_to_next_state(update, context, self.get_next_state(self.reply_summary))

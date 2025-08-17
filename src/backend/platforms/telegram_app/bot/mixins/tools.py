from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.enums import Intensity
from tools.models import Configuration, Tool


class ToolMixin(BaseMixin):
    async def ask_for_tool(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update, Tool.objects.all(), "name", 2, "Choose tool", "", self.get_next_state(self.ask_for_tool)
            ),
        )

    async def save_tool(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.TOOL, Tool, self.get_next_state(self.save_tool)),
        )


class ConfigurationMixin(BaseMixin):
    async def ask_for_configuration(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update,
                Configuration.objects.filter(tool=self.get_context_value(context, Context.TOOL)),
                "name",
                2,
                "Choose configuration",
                "",
                self.get_next_state(self.ask_for_configuration),
            ),
        )

    async def save_configuration(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(
                update, context, Context.CONFIGURATION, Configuration, self.get_next_state(self.save_configuration)
            ),
        )


class IntensityMixin(BaseMixin):
    @sync_to_async
    def _get_tool_intensities_async(self, tool: Tool) -> QuerySet:
        return [Intensity(i.value).name for i in tool.intensities.order_by("value").all()]

    async def ask_for_intensity(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        tool = self.get_context_value(context, Context.TOOL)
        if not tool:
            self.reply(update, "No tool selected")
            return ConversationHandler.END
        values = await self._get_tool_intensities_async(tool) if tool else Intensity.names
        values.reverse()
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_values(update, values, 5, "Choose intensity", self.get_next_state(self.ask_for_intensity)),
        )

    async def save_intensity(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        next_state = await self.go_to_next_state(
            update,
            context,
            await self.save_value(
                update, context, Context.INTENSITY, "Intensity", self.get_next_state(self.save_intensity)
            ),
        )
        if next_state != ConversationHandler.END:
            self.add_context_value(
                context, Context.INTENSITY, (self.get_context_value(context, Context.INTENSITY) or "").upper()
            )
        return await self.go_to_next_state(update, context, next_state)

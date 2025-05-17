from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.enums import Intensity
from tools.models import Configuration, Tool


class ToolMixin(BaseMixin):
    async def _ask_for_tool(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask(
                update,
                Tool.objects.all(),
                "name",
                2,
                "Choose tool",
                "",
                self._get_next_state(self._ask_for_tool),
            ),
        )

    async def _save_tool(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._save(
                update,
                context,
                Context.TOOL,
                Tool,
                self._get_next_state(self._save_tool),
            ),
        )


class ConfigurationMixin(BaseMixin):
    async def _ask_for_configuration(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask(
                update,
                Configuration.objects.filter(tool=self._get_context_value(context, Context.TOOL)),
                "name",
                2,
                "Choose configuration",
                "",
                self._get_next_state(self._ask_for_configuration),
            ),
        )

    async def _save_configuration(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._save(
                update,
                context,
                Context.CONFIGURATION,
                Configuration,
                self._get_next_state(self._save_configuration),
            ),
        )


class IntensityMixin(BaseMixin):
    @sync_to_async
    def _get_tool_intensities_async(self, tool: Tool) -> QuerySet:
        return [Intensity(i.value).name for i in tool.intensities.order_by("value").all()]

    async def _ask_for_intensity(self, update: Update, context: CallbackContext) -> int:
        tool = self._get_context_value(context, Context.TOOL)
        values = await self._get_tool_intensities_async(tool) if tool else Intensity.names
        values.reverse()
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_values(
                update,
                values,
                5,
                "Choose intensity",
                self._get_next_state(self._ask_for_intensity),
            ),
        )

    async def _save_intensity(self, update: Update, context: CallbackContext) -> int:
        next_state = await self._go_to_next_state(
            update,
            context,
            await self._save_value(
                update,
                context,
                Context.INTENSITY,
                "Intensity",
                self._get_next_state(self._save_intensity),
            ),
        )
        if next_state != ConversationHandler.END:
            self._add_context_value(
                context,
                Context.INTENSITY,
                (self._get_context_value(context, Context.INTENSITY) or "").upper(),
            )
        return await self._go_to_next_state(update, context, next_state)

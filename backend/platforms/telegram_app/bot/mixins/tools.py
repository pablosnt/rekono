"""Steps that ask which tool to run, how, and with which intensity.

The tools are shared by all the projects, so they aren't filtered by the project
that the conversation is about, but their configurations and their intensities are
asked for after the tool itself.
"""

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.enums import Intensity
from tools.models import Configuration, Tool


class ToolMixin(BaseMixin):
    """Steps that choose the tool that a task will run."""

    async def ask_for_tool(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose one of the tools.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update, Tool.objects.all(), "name", 2, "Choose tool", "", self.get_next_state(self.ask_for_tool)
            ),
        )

    async def save_tool(self, update: Update, context: CallbackContext) -> int:
        """Remember the tool that the users chose.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step of the conversation.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.TOOL, Tool, self.get_next_state(self.save_tool)),
        )


class ConfigurationMixin(BaseMixin):
    """Steps that choose what the tool of a task will do."""

    async def ask_for_configuration(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose one of the configurations of the tool.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, or the end of the conversation if no
            tool was chosen, since the configurations of every tool would be
            offered otherwise.
        """
        self.validate_update(update)
        tool = self.get_context_value(context, Context.TOOL)
        if not tool:
            await self.reply(update, "No tool selected")
            return ConversationHandler.END
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update,
                Configuration.objects.filter(tool=tool),
                "name",
                2,
                "Choose configuration",
                "",
                self.get_next_state(self.ask_for_configuration),
            ),
        )

    async def save_configuration(self, update: Update, context: CallbackContext) -> int:
        """Remember the configuration that the users chose.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step of the conversation.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(
                update, context, Context.CONFIGURATION, Configuration, self.get_next_state(self.save_configuration)
            ),
        )


class IntensityMixin(BaseMixin):
    """Steps that choose how aggressive a task will be."""

    @sync_to_async
    def _get_tool_intensities_async(self, tool: Tool) -> list[str]:
        """Get the intensities that a tool supports, from the lowest to the highest.

        Args:
            tool: Tool whose intensities are offered to the user.

        Returns:
            The names of the supported intensities, in ascending order.
        """
        return [Intensity(i.value).name for i in tool.intensities.order_by("value").all()]

    async def ask_for_intensity(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose the intensity of the task.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer. Only the intensities that the tool
            supports are offered, or all of them when the task runs a process,
            since each of its tools supports different ones.
        """
        self.validate_update(update)
        tool = self.get_context_value(context, Context.TOOL)
        values = await self._get_tool_intensities_async(tool) if tool else Intensity.names
        values.reverse()
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_values(update, values, 5, "Choose intensity", self.get_next_state(self.ask_for_intensity)),
        )

    async def save_intensity(self, update: Update, context: CallbackContext) -> int:
        """Remember the intensity that the users chose.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step, or the end of the conversation if the users answered
            with nothing, so the following steps never run without an intensity.
        """
        self.validate_update(update)
        next_state = await self.go_to_next_state(
            update,
            context,
            await self.save_value(
                update, context, Context.INTENSITY, "Intensity", self.get_next_state(self.save_intensity)
            ),
        )
        intensity = self.get_context_value(context, Context.INTENSITY)
        if not intensity:
            await self.reply(update, "No intensity selected")
            return ConversationHandler.END
        if next_state != ConversationHandler.END:
            self.add_context_value(context, Context.INTENSITY, intensity.upper())
        return await self.go_to_next_state(update, context, next_state)

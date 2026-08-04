"""Telegram Bot mixins for security tool and configuration management.

Provides mixins for tool selection, configuration management, and intensity
settings in security testing workflows through interactive conversations. Tools,
like processes, are a global catalog rather than project-scoped. ConfigurationMixin
expects Context.TOOL to already be set by ToolMixin, since configurations are listed
for that tool. IntensityMixin also reads Context.TOOL when present to narrow the
choices to that tool's supported intensities, but works without it, falling back to
every Intensity value, which is how the Process conversation uses it without a tool.
"""

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.enums import Intensity
from tools.models import Configuration, Tool


class ToolMixin(BaseMixin):
    """Mixin providing security tool selection functionality.

    Enables conversations to display available security tools and handle
    tool selection for security testing operations.
    """

    async def ask_for_tool(self, update: Update, context: CallbackContext) -> int:
        """Display security tool selection options.

        Shows a list of available security tools for selection in testing workflows.

        Args:
            update (Update): The Telegram update containing the user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state based on tool selection.
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
        """Save selected security tool to conversation context.

        Processes the user's tool selection and stores it in the conversation
        context for use in subsequent configuration steps.

        Args:
            update (Update): The Telegram update containing user selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after tool selection.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.TOOL, Tool, self.get_next_state(self.save_tool)),
        )


class ConfigurationMixin(BaseMixin):
    """Mixin providing tool configuration selection functionality.

    Enables conversations to display available configurations for selected
    security tools and handle configuration selection.
    """

    async def ask_for_configuration(self, update: Update, context: CallbackContext) -> int:
        """Display tool configuration selection options.

        Shows available configurations for the selected security tool. The
        conversation ends when no tool has been selected yet, since listing
        configurations without a tool would offer every configuration in Rekono.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state based on configuration selection.
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
        """Save selected tool configuration to conversation context.

        Processes the user's configuration selection and stores it in the conversation
        context for use in security testing execution.

        Args:
            update (Update): The Telegram update containing user selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after configuration selection.
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
    """Mixin providing intensity level selection functionality.

    Enables conversations to display available intensity levels for selected
    security tools and handle intensity selection.
    """

    @sync_to_async
    def _get_tool_intensities_async(self, tool: Tool) -> list[str]:
        """Get available intensity levels for a security tool (async wrapper).

        Args:
            tool (Tool): The security tool to get intensities for.

        Returns:
            list[str]: Intensity level names supported by the tool, ordered by value.
        """
        return [Intensity(i.value).name for i in tool.intensities.order_by("value").all()]

    async def ask_for_intensity(self, update: Update, context: CallbackContext) -> int:
        """Display intensity level selection options.

        Shows the intensity levels supported by the selected tool, in descending order. When
        no tool is in context, as in the Process conversation, every intensity level is
        offered instead.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state.
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
        """Save selected intensity level to conversation context.

        Processes the user's intensity selection, converts to uppercase,
        and stores it in the conversation context for security testing execution.
        The conversation ends when nothing was stored, so the next states never
        run with a missing intensity.

        Args:
            update (Update): The Telegram update containing user selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after intensity selection.
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

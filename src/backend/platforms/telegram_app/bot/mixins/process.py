"""Telegram Bot mixin for security process selection workflows.

Provides process selection functionality for conversations that require
process context including process listing, selection, and context storage.
"""

from telegram import Update
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from processes.models import Process


class ProcessMixin(BaseMixin):
    """Mixin providing security process selection functionality.

    Enables conversations to display available security processes and handle
    process selection for security testing workflows.
    """
    async def ask_for_process(self, update: Update, context: CallbackContext) -> int:
        """Display security process selection options.

        Shows a list of available security processes for selection in testing workflows.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state based on process selection.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update,
                Process.objects.all(),
                "name",
                2,
                "Choose process",
                "There are no processes\. Go to Rekono to create one",
                self.get_next_state(self.ask_for_process),
            ),
        )

    async def save_process(self, update: Update, context: CallbackContext) -> int:
        """Save selected process to conversation context.

        Processes the user's process selection and stores it in the conversation
        context for use in subsequent security testing steps.

        Args:
            update (Update): The Telegram update containing user selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after process selection.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.PROCESS, Process, self.get_next_state(self.save_process)),
        )

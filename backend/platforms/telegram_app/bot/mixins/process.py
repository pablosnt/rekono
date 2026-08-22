"""Steps that ask which process a task must run.

The processes are shared by all the projects, so they aren't filtered by the
project that the conversation is about.
"""

from telegram import Update
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from processes.models import Process


class ProcessMixin(BaseMixin):
    """Steps that choose the process that a task will run."""

    async def ask_for_process(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose one of the processes.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, or the end of the conversation if
            there is no process at all.
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
        """Remember the process that the users chose.

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
            await self.save(update, context, Context.PROCESS, Process, self.get_next_state(self.save_process)),
        )

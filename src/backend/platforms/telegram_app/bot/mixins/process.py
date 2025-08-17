from telegram import Update
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from processes.models import Process


class ProcessMixin(BaseMixin):
    async def ask_for_process(self, update: Update, context: CallbackContext) -> int:
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
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.PROCESS, Process, self.get_next_state(self.save_process)),
        )

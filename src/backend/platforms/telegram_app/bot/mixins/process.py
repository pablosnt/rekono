from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from processes.models import Process
from telegram import Update
from telegram.ext import CallbackContext


class ProcessMixin(BaseMixin):
    async def _ask_for_process(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask(
                update,
                Process.objects.all(),
                "name",
                2,
                "Choose process",
                "There are no processes\. Go to Rekono to create one",
                self._get_next_state(self._ask_for_process),
            ),
        )

    async def _save_process(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._save(
                update,
                context,
                Context.PROCESS,
                Process,
                self._get_next_state(self._save_process),
            ),
        )

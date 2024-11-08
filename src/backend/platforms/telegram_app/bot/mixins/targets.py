from telegram import Update
from telegram.ext import CallbackContext

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from targets.models import Target
from targets.serializers import TargetSerializer


class TargetMixin(BaseMixin):
    async def _ask_for_target(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask(
                update,
                Target.objects.filter(
                    project=self._get_context_value(context, Context.PROJECT)
                ).all(),
                "target",
                3,
                "Choose target",
                "There are no targets in the selected project\. Use /newtarget to create one",
                self._get_next_state(self._ask_for_target),
            ),
        )

    async def _save_target(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._save(
                update,
                context,
                Context.TARGET,
                Target,
                self._get_next_state(self._save_target),
            ),
        )

    async def _ask_for_new_target(
        self, update: Update, context: CallbackContext
    ) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_for_new_attribute(
                update,
                "target",
                "target",
                self._get_next_state(self._ask_for_new_target),
            ),
        )

    async def _create_target(self, update: Update, context: CallbackContext) -> int:
        project = self._get_context_value(context, Context.PROJECT)
        next_state, instance = await self._create(
            update,
            context,
            TargetSerializer,
            {
                "project": project.id if project else None,
                "target": (
                    update.effective_message.text if update.effective_message else None
                ),
            },
            self._get_previous_state(self._create_target),
            self._get_next_state(self._create_target),
        )
        if instance:
            await self._reply(
                update,
                f"New target *{self._escape(instance.target)}* \(_{self._escape(instance.type)}_\) has been created in project *{self._escape(instance.project.name)}*",
            )
        return await self._go_to_next_state(update, context, next_state)

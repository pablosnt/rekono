from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from targets.models import Target
from targets.serializers import TargetSerializer


class TargetMixin(BaseMixin):
    async def ask_for_target(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update,
                Target.objects.filter(project=self.get_context_value(context, Context.PROJECT)).all(),
                "target",
                3,
                "Choose target",
                "There are no targets in the selected project\. Use /newtarget to create one",
                self.get_next_state(self.ask_for_target),
            ),
        )

    async def save_target(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.TARGET, Target, self.get_next_state(self.save_target)),
        )

    async def ask_for_new_target(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_for_new_attribute(update, "target", "target", self.get_next_state(self.ask_for_new_target)),
        )

    async def create_target(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        project = self.get_context_value(context, Context.PROJECT)
        if not project:
            self.reply(update, "No project selected")
            return ConversationHandler.END
        next_state, instance = await self._create(
            update,
            context,
            TargetSerializer,
            {"project": project.id, "target": update.effective_message.text if update.effective_message else None},
            self.get_previous_state(self.create_target),
            self.get_next_state(self.create_target),
        )
        if instance:
            await self.reply(
                update,
                f"New target *{self.escape(instance.target)}* \(_{self.escape(instance.type)}_\) has been created in project *{self.escape(instance.project.name)}*",
            )
        return await self.go_to_next_state(update, context, next_state)

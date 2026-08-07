"""Steps that ask which target a conversation is about, or create a new one.

The targets belong to a project, so these steps need the project to have been
chosen before.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from targets.models import Target
from targets.serializers import TargetSerializer


class TargetMixin(BaseMixin):
    """Steps that choose the target of a conversation, or create it."""

    async def ask_for_target(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose one of the targets of the project.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, or the end of the conversation if the
            chat can't run the command, if no project was chosen, or if the project
            has no target yet.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        project = self.get_context_value(context, Context.PROJECT)
        if not project:
            await self.reply(update, "No project selected")
            return ConversationHandler.END
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update,
                Target.objects.filter(project=project, project__members=chat.user).all(),
                "target",
                3,
                "Choose target",
                "There are no targets in the selected project\. Use /newtarget to create one",
                self.get_next_state(self.ask_for_target),
            ),
        )

    async def save_target(self, update: Update, context: CallbackContext) -> int:
        """Remember the target that the users chose.

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
            await self.save(update, context, Context.TARGET, Target, self.get_next_state(self.save_target)),
        )

    async def ask_for_new_target(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to write the target that they want to create.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that creates the target.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_for_new_attribute(update, "target", "target", self.get_next_state(self.ask_for_new_target)),
        )

    async def create_target(self, update: Update, context: CallbackContext) -> int:
        """Create the target that the users wrote in the chosen project.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step, the previous one if what the users wrote isn't a valid
            target, or the end of the conversation if no project was chosen.
        """
        self.validate_update(update)
        project = self.get_context_value(context, Context.PROJECT)
        if not project:
            await self.reply(update, "No project selected")
            return ConversationHandler.END
        next_state, instance = await self.create(
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
        return await self.go_to_next_state(update, context, next_state, invoke_next_state=instance is None)

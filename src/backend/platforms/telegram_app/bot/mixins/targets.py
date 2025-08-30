"""Telegram Bot mixin for target selection and management workflows.

Provides target selection and creation functionality for conversations
that require target context including target listing, creation, and validation.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from targets.models import Target
from targets.serializers import TargetSerializer


class TargetMixin(BaseMixin):
    """Mixin providing target selection and creation functionality.

    Enables conversations to display target lists, handle target selection,
    and create new targets within the selected project context.
    """

    async def ask_for_target(self, update: Update, context: CallbackContext) -> int:
        """Display target selection options within the current project.

        Shows a list of targets available in the selected project and allows
        selection for use in security testing operations.

        Args:
            update (Update): The Telegram update containing the user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state based on target availability.
        """
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
        """Save selected target to conversation context.

        Processes the user's target selection and stores it in the conversation
        context for use in subsequent security testing operations.

        Args:
            update (Update): The Telegram update containing user selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after target selection.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.TARGET, Target, self.get_next_state(self.save_target)),
        )

    async def ask_for_new_target(self, update: Update, context: CallbackContext) -> int:
        """Prompt user to input a new target identifier.

        Requests user to provide target identifier for target creation
        within the selected project.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for target input processing.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_for_new_attribute(update, "target", "target", self.get_next_state(self.ask_for_new_target)),
        )

    async def create_target(self, update: Update, context: CallbackContext) -> int:
        """Create new target from user input with project validation.

        Processes user input to create a target within the selected project,
        validates project context, and displays creation confirmation.

        Args:
            update (Update): The Telegram update containing target input.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after target creation or ConversationHandler.END.
        """
        self.validate_update(update)
        project = self.get_context_value(context, Context.PROJECT)
        if not project:
            self.reply(update, "No project selected")
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
        return await self.go_to_next_state(update, context, next_state)

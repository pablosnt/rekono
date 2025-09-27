"""Telegram Bot mixin for project selection and management workflows.

Provides project selection functionality for conversations that require
project context including project listing, selection, and context storage.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from projects.models import Project


class ProjectMixin(BaseMixin):
    """Mixin providing project selection functionality for bot conversations.

    Enables conversations to display project lists and handle project selection
    for users with appropriate permissions.
    """

    async def ask_for_project(self, update: Update, context: CallbackContext) -> int:
        """Display project selection options to the user.

        Shows a list of projects that the user is a member of and allows
        selection for use in subsequent conversation steps.

        Args:
            update (Update): The Telegram update containing the user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state or ConversationHandler.END if no chat.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        return await self.go_to_next_state(
            update,
            context,
            await self.ask(
                update,
                Project.objects.filter(members=chat.user).all(),
                "name",
                3,
                "Choose project",
                "You have no projects\. Go to Rekono to create one or ask your administrator to assign you one",
                self.get_next_state(self.ask_for_project),
                chat,
            ),
        )

    async def save_project(self, update: Update, context: CallbackContext) -> int:
        """Save the selected project to conversation context.

        Processes the user's project selection and stores it in the conversation
        context for use in subsequent steps.

        Args:
            update (Update): The Telegram update containing the user selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state or ConversationHandler.END if no chat.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        next_state = await self.save(
            update,
            context,
            Context.PROJECT,
            Project,
            self.get_next_state(self.save_project),
            chat,
        )
        project = self.get_context_value(context, Context.PROJECT)
        if project:
            await self.reply(update, f"💼 _Project_   *{self.escape(project.name)}*")
        return await self.go_to_next_state(update, context, next_state)

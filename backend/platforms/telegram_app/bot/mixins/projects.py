"""Steps that ask which project a conversation is about.

This is always the first step of a conversation, since everything that the other
steps ask about belongs to a project, and it's the only answer that survives the
conversation, so the users don't have to choose it again and again.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from projects.models import Project


class ProjectMixin(BaseMixin):
    """Steps that choose the project that a conversation is about."""

    async def ask_for_project(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose one of the projects that they belong to.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, or the end of the conversation if the
            chat can't run the command or if the user belongs to no project.
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
        """Remember the project that the users chose.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step, or the end of the conversation if the chat can't run
            the command.
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

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from projects.models import Project


class ProjectMixin(BaseMixin):
    async def ask_for_project(self, update: Update, context: CallbackContext) -> int:
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

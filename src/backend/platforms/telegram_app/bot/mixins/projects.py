from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from projects.models import Project


class ProjectMixin(BaseMixin):
    async def _ask_for_project(self, update: Update, context: CallbackContext) -> int:
        chat = await self._get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        return await self._go_to_next_state(
            update,
            context,
            await self._ask(
                update,
                Project.objects.filter(members=chat.user).all(),
                "name",
                3,
                "Choose project",
                "You have no projects\. Go to Rekono to create one or ask your administrator to assign you one",
                self._get_next_state(self._ask_for_project),
                chat,
            ),
        )

    async def _save_project(self, update: Update, context: CallbackContext) -> int:
        chat = await self._get_active_telegram_chat(update)
        next_state = await self._save(
            update,
            context,
            Context.PROJECT,
            Project,
            self._get_next_state(self._save_project),
            chat,
        )
        project = self._get_context_value(context, Context.PROJECT)
        if project:
            await self._reply(update, f"💼 _Project_   *{self._escape(project.name)}*")
        return await self._go_to_next_state(update, context, next_state)

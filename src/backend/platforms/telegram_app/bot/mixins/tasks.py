from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tasks.serializers import TaskSerializer
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


class TaskMixin(BaseMixin):
    yes = "👍 Yes"
    no = "👎 No"

    async def _ask_for_task_confirmation(
        self, update: Update, context: CallbackContext
    ) -> int:
        project = self._get_context_value(context, Context.PROJECT)
        target = self._get_context_value(context, Context.TARGET)
        process = self._get_context_value(context, Context.PROCESS)
        tool = self._get_context_value(context, Context.TOOL)
        configuration = self._get_context_value(context, Context.CONFIGURATION)
        intensity = self._get_context_value(context, Context.INTENSITY)
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_values(
                update,
                [self.yes, self.no],
                2,
                f"""
The following task will be executed:

💼 _Project_   *{self._escape(project.name) if project else None}*
🎯 _Target_    *{self._escape(target.target) if target else None}*
{f'🔄 _Process_   *{self._escape(process.name)}*' if process else
f'''🛠 _Tool_       *{self._escape(tool.name)}*
⚙️ _Configuration_  *{self._escape(configuration.name)}*'''}
🔊 _Intensity_ *{self._escape(intensity)}*

Are you sure?
                """,
                self._get_next_state(self._ask_for_task_confirmation),
            ),
        )

    async def _new_task(self, update: Update, context: CallbackContext) -> int:
        chat = await self._get_active_telegram_chat(update)
        next_state = ConversationHandler.END
        if chat and update.callback_query and update.callback_query.data:
            if update.callback_query.data == self.yes:
                target = self._get_context_value(context, Context.TARGET)
                process = self._get_context_value(context, Context.PROCESS)
                configuration = self._get_context_value(context, Context.CONFIGURATION)
                wordlist = self._get_context_value(context, Context.WORDLIST)
                data = {
                    "target_id": target.id if target else None,
                    "intensity": self._get_context_value(
                        context, Context.INTENSITY
                    ).capitalize(),
                    "executor": chat.user,
                    "wordlists": [wordlist.id] if wordlist else [],
                }
                if process:
                    data["process_id"] = process.id
                elif configuration:
                    data["configuration_id"] = configuration.id
                next_state, instance = await self._create(
                    update,
                    context,
                    TaskSerializer,
                    data,
                    self._get_previous_state(self._new_task),
                    self._get_next_state(self._new_task),
                    chat,
                )
                if instance:
                    self._remove_all_context_values(context)
                    await self._reply(
                        update, f"✅ Task {instance.id} created successfully\!"
                    )
            else:
                self._remove_all_context_values(context)
                await self._reply(update, "❌ Task has been cancelled")
        return await self._go_to_next_state(update, context, next_state)

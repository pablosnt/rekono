"""Telegram Bot mixin for security task execution confirmation and creation.

Provides task confirmation prompts and task creation functionality for
security testing workflows including validation and execution setup. Runs last in
every conversation that creates a Task (Tool and Process), after all the other
mixins have populated the context values it reads. On completion it clears the
whole conversation context, ending the flow either with a created Task or with
the user's cancellation.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tasks.models import Task
from tasks.serializers import TaskSerializer


class TaskMixin(BaseMixin):
    """Mixin providing security task confirmation and creation functionality.

    Enables conversations to display task summaries, confirm execution parameters,
    and create security testing tasks with proper validation.

    Attributes:
        yes (str): Confirmation button text with emoji.
        no (str): Rejection button text with emoji.
    """

    yes = "👍 Yes"
    no = "👎 No"

    async def ask_for_task_confirmation(self, update: Update, context: CallbackContext) -> int:
        """Display task confirmation prompt with execution summary.

        Shows a comprehensive summary of the security task to be executed
        including project, target, tool/process, and intensity settings. The target
        line uses Task.get_target(target, target_port), the shared label helper that
        also builds target labels for execution notifications, so it renders as
        "<target>:<port><path>" when a target port was selected, or the bare target
        otherwise. Validates that all required parameters are present, and the
        configuration only counts as valid when its tool is also in the context,
        because the summary shows both names.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for confirmation or ConversationHandler.END.
        """
        self.validate_update(update)
        project = self.get_context_value(context, Context.PROJECT)
        target = self.get_context_value(context, Context.TARGET)
        target_port = self.get_context_value(context, Context.TARGET_PORT)
        process = self.get_context_value(context, Context.PROCESS)
        tool = self.get_context_value(context, Context.TOOL)
        configuration = self.get_context_value(context, Context.CONFIGURATION)
        intensity = self.get_context_value(context, Context.INTENSITY)
        for condition, text in [
            (project, "project"),
            (target, "target"),
            (process or (tool and configuration), "process or configuration"),
            (intensity, "intensity"),
        ]:
            if not condition:
                await self.reply(update, f"No {text} selected")
                return ConversationHandler.END
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_values(
                update,
                [self.yes, self.no],
                2,
                f"""
The following task will be executed:

💼 _Project_   *{self.escape(project.name)}*
🎯 _Target_    *{self.escape(Task.get_target(target, target_port))}*
{
                    f"🔄 _Process_   *{self.escape(process.name)}*"
                    if process
                    else f'''🛠 _Tool_       *{self.escape(tool.name)}*
⚙️ _Configuration_  *{self.escape(configuration.name)}*'''
                }
🔊 _Intensity_ *{self.escape(intensity)}*

Are you sure?
                """,
                self.get_next_state(self.ask_for_task_confirmation),
            ),
        )

    async def new_task(self, update: Update, context: CallbackContext) -> int:
        """Create a new security task based on user confirmation.

        Processes user confirmation and creates a security task with all
        configured parameters including target, tool/process, intensity,
        and optional wordlists and input parameters. The required values are
        checked again here instead of trusting the confirmation step, since the
        user can answer an old confirmation message whose conversation context
        no longer holds them.

        Args:
            update (Update): The Telegram update containing user confirmation.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: ConversationHandler.END after task creation or cancellation.
        """
        chat = await self.get_active_telegram_chat(update)
        next_state = ConversationHandler.END
        instance = None
        if chat and update.callback_query and update.callback_query.data:
            if update.callback_query.data == self.yes:
                target = self.get_context_value(context, Context.TARGET)
                target_port = self.get_context_value(context, Context.TARGET_PORT)
                process = self.get_context_value(context, Context.PROCESS)
                configuration = self.get_context_value(context, Context.CONFIGURATION)
                intensity = self.get_context_value(context, Context.INTENSITY)
                wordlist = self.get_context_value(context, Context.WORDLIST)
                input_technology = self.get_context_value(context, Context.INPUT_TECHNOLOGY)
                input_vulnerability = self.get_context_value(context, Context.INPUT_VULNERABILITY)
                for condition, text in [
                    (target, "target"),
                    (process or configuration, "process or configuration"),
                    (intensity, "intensity"),
                ]:
                    if not condition:
                        await self.reply(update, f"No {text} selected")
                        return ConversationHandler.END
                data = {
                    "target_id": target.id,
                    "intensity": intensity.capitalize(),
                    "executor": chat.user,
                    "wordlists": [wordlist.id] if wordlist else [],
                    "input_technologies": [input_technology.id] if input_technology else [],
                    "input_vulnerabilities": [input_vulnerability.id] if input_vulnerability else [],
                }
                if target_port:
                    data["target_port_id"] = target_port.id
                if process:
                    data["process_id"] = process.id
                elif configuration:
                    data["configuration_id"] = configuration.id
                next_state, instance = await self.create(
                    update,
                    context,
                    TaskSerializer,
                    data,
                    self.get_previous_state(self.new_task),
                    self.get_next_state(self.new_task),
                    chat,
                )
                if instance:
                    self.remove_all_context_values(context)
                    await self.reply(update, f"✅ Task \#{instance.id} created successfully\!")
            else:
                self.remove_all_context_values(context)
                await self.reply(update, "❌ Task has been cancelled")
        return await self.go_to_next_state(update, context, next_state, invoke_next_state=instance is None)

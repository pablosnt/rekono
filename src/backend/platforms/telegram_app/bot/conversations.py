from typing import Any, Callable

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context, Section
from platforms.telegram_app.bot.framework import BaseTelegramBot
from platforms.telegram_app.bot.mixins.authentications import AuthenticationMixin
from platforms.telegram_app.bot.mixins.parameters import (
    InputTechnologyMixin,
    InputVulnerabilityMixin,
)
from platforms.telegram_app.bot.mixins.process import ProcessMixin
from platforms.telegram_app.bot.mixins.projects import ProjectMixin
from platforms.telegram_app.bot.mixins.target_ports import TargetPortMixin
from platforms.telegram_app.bot.mixins.targets import TargetMixin
from platforms.telegram_app.bot.mixins.tasks import TaskMixin
from platforms.telegram_app.bot.mixins.tools import (
    ConfigurationMixin,
    IntensityMixin,
    ToolMixin,
)
from platforms.telegram_app.bot.mixins.wordlists import WordlistMixin
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)


class BaseConversation(ConversationHandler, BaseTelegramBot):
    _states_methods: list[Callable] = []
    first_state = 0

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            entry_points=[CommandHandler(self.get_name(), self._save_command_name)],
            states={
                index: [
                    (
                        MessageHandler(filters.TEXT, state_method)
                        if state_method.__name__.startswith("_create_")
                        else CallbackQueryHandler(state_method)
                    )
                ]
                for index, state_method in enumerate(self._states_methods)
            },
            fallbacks=[Cancel()],
        )

    async def _save_command_name(self, update: Update, context: CallbackContext) -> int:
        self._add_context_value(context, Context.COMMAND, self.get_name())
        return await self._states_methods[0](update, context)


class SelectProject(BaseConversation, ProjectMixin):
    help = "Select one project to be used in next commands"
    section = Section.SELECTION

    def __init__(self, **kwargs: Any) -> None:
        self._states_methods = [self._ask_for_project, self._save_project]
        super().__init__(**kwargs)


class BaseConversationFromProject(BaseConversation, ProjectMixin):
    async def _ask_for_project(self, update: Update, context: CallbackContext) -> int:
        return (
            await super()._ask_for_project(update, context)
            if not self._get_context_value(context, Context.PROJECT)
            else await self._go_to_next_state(
                update, context, self._get_next_state(self._save_project)
            )
        )


class NewTarget(BaseConversationFromProject, TargetMixin):
    help = "Create new target"
    section = Section.TARGETS

    def __init__(self, **kwargs: Any) -> None:
        self._states_methods = [
            self._ask_for_project,
            self._save_project,
            self._ask_for_new_target,
            self._create_target,
        ]
        super().__init__(**kwargs)


class NewPort(
    BaseConversationFromProject, TargetMixin, TargetPortMixin, AuthenticationMixin
):
    help = "Create new target port"
    section = Section.TARGETS

    def __init__(self, **kwargs: Any) -> None:
        self._states_methods = [
            self._ask_for_project,
            self._save_project,
            self._ask_for_target,
            self._save_target,
            self._ask_for_new_target_port,
            self._create_target_port,
            self._ask_for_authentication_type,
            self._save_authentication_type,
            self._ask_for_new_authentication,
            self._create_authentication,
            self._reply_summary,
        ]
        super().__init__(**kwargs)


class Tool(
    BaseConversationFromProject,
    TargetMixin,
    ToolMixin,
    ConfigurationMixin,
    IntensityMixin,
    WordlistMixin,
    InputTechnologyMixin,
    InputVulnerabilityMixin,
    TaskMixin,
):
    help = "Execute a tool"
    section = Section.TASKS

    def __init__(self, **kwargs: Any) -> None:
        self._states_methods = [
            self._ask_for_project,
            self._save_project,
            self._ask_for_target,
            self._save_target,
            self._ask_for_tool,
            self._save_tool,
            self._ask_for_configuration,
            self._save_configuration,
            self._ask_for_intensity,
            self._save_intensity,
            self._ask_for_wordlist,
            self._save_wordlist,
            self._ask_for_input_technology,
            self._save_input_technology,
            self._create_input_technology,
            self._ask_for_input_vulnerability,
            self._save_input_vulnerability,
            self._create_input_vulnerability,
            self._ask_for_task_confirmation,
            self._new_task,
        ]
        super().__init__(**kwargs)


class Process(
    BaseConversationFromProject,
    TargetMixin,
    ProcessMixin,
    IntensityMixin,
    WordlistMixin,
    TaskMixin,
):
    help = "Execute a process"
    section = Section.TASKS

    def __init__(self, **kwargs: Any) -> None:
        self._states_methods = [
            self._ask_for_project,
            self._save_project,
            self._ask_for_target,
            self._save_target,
            self._ask_for_process,
            self._save_process,
            self._ask_for_intensity,
            self._save_intensity,
            self._ask_for_wordlist,
            self._save_wordlist,
            self._ask_for_task_confirmation,
            self._new_task,
        ]
        super().__init__(**kwargs)

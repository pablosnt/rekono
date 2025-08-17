from functools import cached_property
from typing import Any, Callable

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context, Section
from platforms.telegram_app.bot.framework import BaseTelegramBot
from platforms.telegram_app.bot.mixins.authentications import AuthenticationMixin
from platforms.telegram_app.bot.mixins.parameters import InputTechnologyMixin, InputVulnerabilityMixin
from platforms.telegram_app.bot.mixins.process import ProcessMixin
from platforms.telegram_app.bot.mixins.projects import ProjectMixin
from platforms.telegram_app.bot.mixins.target_ports import TargetPortMixin
from platforms.telegram_app.bot.mixins.targets import TargetMixin
from platforms.telegram_app.bot.mixins.tasks import TaskMixin
from platforms.telegram_app.bot.mixins.tools import ConfigurationMixin, IntensityMixin, ToolMixin
from platforms.telegram_app.bot.mixins.wordlists import WordlistMixin


class BaseConversation(ConversationHandler, BaseTelegramBot):
    first_state = 0

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            entry_points=[CommandHandler(self.name, self._save_command_name)],
            states={
                index: [
                    (
                        MessageHandler(filters.TEXT, state_method)
                        if state_method.__name__.startswith("_create_")
                        else CallbackQueryHandler(state_method)
                    )
                ]
                for index, state_method in enumerate(self.states_methods)
            },
            fallbacks=[Cancel()],
        )

    @cached_property
    def states_methods(self) -> list[Callable]:
        return []

    async def _save_command_name(self, update: Update, context: CallbackContext) -> int:
        self.add_context_value(context, Context.COMMAND, self.name)
        return await self.states_methods[0](update, context)


class SelectProject(BaseConversation, ProjectMixin):
    help = "Select one project to be used in next commands"
    section = Section.SELECTION

    @cached_property
    def states_methods(self) -> list[Callable]:
        return [self.ask_for_project, self.save_project]


class BaseConversationFromProject(BaseConversation, ProjectMixin):
    async def ask_for_project(self, update: Update, context: CallbackContext) -> int:
        return (
            await super().ask_for_project(update, context)
            if not self.get_context_value(context, Context.PROJECT)
            else await self.go_to_next_state(update, context, self.get_next_state(self.save_project))
        )


class NewTarget(BaseConversationFromProject, TargetMixin):
    help = "Create new target"
    section = Section.TARGETS

    @cached_property
    def states_methods(self) -> list[Callable]:
        return [self.ask_for_project, self.save_project, self.ask_for_new_target, self.create_target]


class NewPort(BaseConversationFromProject, TargetMixin, TargetPortMixin, AuthenticationMixin):
    help = "Create new target port"
    section = Section.TARGETS

    @cached_property
    def states_methods(self) -> list[Callable]:
        return [
            self.ask_for_project,
            self.save_project,
            self.ask_for_target,
            self.save_target,
            self.ask_for_new_target_port,
            self.create_target_port,
            self.ask_for_authentication_type,
            self.save_authentication_type,
            self.ask_for_new_authentication,
            self.create_authentication,
            self.reply_summary,
        ]


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

    @cached_property
    def states_methods(self) -> list[Callable]:
        return [
            self.ask_for_project,
            self.save_project,
            self.ask_for_target,
            self.save_target,
            self.ask_for_tool,
            self.save_tool,
            self.ask_for_configuration,
            self.save_configuration,
            self.ask_for_intensity,
            self.save_intensity,
            self.ask_for_wordlist,
            self.save_wordlist,
            self.ask_for_input_technology,
            self.save_input_technology,
            self.create_input_technology,
            self.ask_for_input_vulnerability,
            self.save_input_vulnerability,
            self.create_input_vulnerability,
            self.ask_for_task_confirmation,
            self.new_task,
        ]


class Process(BaseConversationFromProject, TargetMixin, ProcessMixin, IntensityMixin, WordlistMixin, TaskMixin):
    help = "Execute a process"
    section = Section.TASKS

    @cached_property
    def states_methods(self) -> list[Callable]:
        return [
            self.ask_for_project,
            self.save_project,
            self.ask_for_target,
            self.save_target,
            self.ask_for_process,
            self.save_process,
            self.ask_for_intensity,
            self.save_intensity,
            self.ask_for_wordlist,
            self.save_wordlist,
            self.ask_for_task_confirmation,
            self.new_task,
        ]

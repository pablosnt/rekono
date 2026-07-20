"""Telegram Bot conversation implementations for complex security workflows.

Provides conversation-based interactions for multi-step security testing
operations including project management, target configuration, and tool execution
through interactive Telegram Bot workflows.
"""

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
    """Base class for multi-step conversation workflows.

    Provides the foundation for complex conversation-based interactions
    combining ConversationHandler with bot framework capabilities for
    multi-state security testing workflows.

    Attributes:
        first_state (int): The initial state index for conversations.
    """

    first_state = 0

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the conversation with entry points, states, and fallbacks.

        Sets up the conversation handler with automatic state mapping based
        on method names. Methods starting with 'create_' use MessageHandler
        for text input, others use CallbackQueryHandler for button interactions.

        Args:
            **kwargs: Additional keyword arguments for ConversationHandler.
        """
        super().__init__(
            entry_points=[CommandHandler(self.command_name, self.save_command_name)],
            states={
                index: [
                    (
                        MessageHandler(filters.TEXT, state_method)
                        if state_method.__name__.startswith("create_")
                        else CallbackQueryHandler(state_method)
                    )
                ]
                for index, state_method in enumerate(self.states_methods)
            },
            fallbacks=[Cancel()],
        )

    @cached_property
    def states_methods(self) -> list[Callable]:
        """Get the list of conversation state methods.

        Override this property to define the sequence of methods that
        represent the conversation states.

        Returns:
            list[Callable]: List of methods representing conversation states.
        """
        return []

    async def save_command_name(self, update: Update, context: CallbackContext) -> int:
        """Save the command name to context and start the conversation.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: The result of the first state method execution.
        """
        await self.log_command_execution(update, self.command_name)
        self.add_context_value(context, Context.COMMAND, self.command_name)
        return await self.states_methods[0](update, context)


class SelectProject(BaseConversation, ProjectMixin):
    """Conversation for selecting a project to use in subsequent operations.

    Provides an interactive workflow for users to select a project from their
    available projects and save it to the conversation context.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (PROJECTS).
    """

    help = "Select one project to be used in next commands"
    section = Section.PROJECTS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """Define the conversation flow for project selection.

        Returns:
            list[Callable]: List of methods for project selection workflow.
        """
        return [self.ask_for_project, self.save_project]


class BaseConversationFromProject(BaseConversation, ProjectMixin):
    """Base class for conversations that require a project context.

    Extends BaseConversation with project selection logic, automatically
    handling project selection if no project is currently selected.
    """

    async def ask_for_project(self, update: Update, context: CallbackContext) -> int:
        """Ask for project selection if none is currently selected.

        Args:
            update (Update): The Telegram update containing the command.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next state index based on project availability.
        """
        return (
            await super().ask_for_project(update, context)
            if not self.get_context_value(context, Context.PROJECT)
            else await self.go_to_next_state(
                update, context, self.get_next_state(self.save_project), invoke_next_state=True
            )
        )


class NewTarget(BaseConversationFromProject, TargetMixin):
    """Conversation for creating new security testing targets.

    Provides an interactive workflow for users to create new targets
    within a selected project for security testing operations.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (TARGETS).
    """

    help = "Create new target"
    section = Section.TARGETS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """Define the conversation flow for target creation.

        Returns:
            list[Callable]: List of methods for target creation workflow.
        """
        return [self.ask_for_project, self.save_project, self.ask_for_new_target, self.create_target]


class NewPort(BaseConversationFromProject, TargetMixin, TargetPortMixin, AuthenticationMixin):
    """Conversation for creating new target ports with authentication.

    Provides a comprehensive workflow for creating target ports including
    port configuration and optional authentication setup for security testing.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (TARGETS).
    """

    help = "Create new target port"
    section = Section.TARGETS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """Define the conversation flow for target port creation.

        Returns:
            list[Callable]: List of methods for port and authentication setup.
        """
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
    TargetPortMixin,
    ToolMixin,
    ConfigurationMixin,
    IntensityMixin,
    WordlistMixin,
    InputTechnologyMixin,
    InputVulnerabilityMixin,
    TaskMixin,
):
    """Conversation for executing individual security tools.

    Provides a comprehensive workflow for configuring and executing security
    tools including target selection, tool configuration, intensity settings,
    wordlist selection, and input parameter configuration.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (TASKS).
    """

    help = "Execute a tool"
    section = Section.TASKS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """Define the comprehensive conversation flow for tool execution.

        Returns:
            list[Callable]: List of methods for complete tool configuration workflow.
        """
        return [
            self.ask_for_project,
            self.save_project,
            self.ask_for_target,
            self.save_target,
            self.ask_for_target_port,
            self.save_target_port,
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


class Process(
    BaseConversationFromProject, TargetMixin, TargetPortMixin, ProcessMixin, IntensityMixin, WordlistMixin, TaskMixin
):
    """Conversation for executing security testing processes.

    Provides a workflow for configuring and executing predefined security
    testing processes including process selection, intensity configuration,
    and wordlist selection for automated security assessments.

    Attributes:
        help (str): Command help text displayed in command list.
        section (Section): Command section for organization (TASKS).
    """

    help = "Execute a process"
    section = Section.TASKS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """Define the conversation flow for process execution.

        Returns:
            list[Callable]: List of methods for process configuration workflow.
        """
        return [
            self.ask_for_project,
            self.save_project,
            self.ask_for_target,
            self.save_target,
            self.ask_for_target_port,
            self.save_target_port,
            self.ask_for_process,
            self.save_process,
            self.ask_for_intensity,
            self.save_intensity,
            self.ask_for_wordlist,
            self.save_wordlist,
            self.ask_for_task_confirmation,
            self.new_task,
        ]

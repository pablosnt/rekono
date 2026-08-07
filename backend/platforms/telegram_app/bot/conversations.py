"""Bot commands that need to ask several things before doing anything.

A conversation is a list of steps that ask for something and save what the user
answers, so adding a step to a command is only adding a method to its list.
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
    """Base conversation that the bot has with a user.

    Attributes:
        first_state: Position of the first step of a conversation.
    """

    first_state = 0

    def __init__(self, **kwargs: Any) -> None:
        """Prepare the conversation with the steps that it's made of.

        Args:
            **kwargs: Not used, since a conversation is always built from its own
              steps.
        """
        super().__init__(
            entry_points=[CommandHandler(self.command_name, self.save_command_name)],
            # The steps whose name starts with create_ are the ones that ask the users to
            # write something, the rest are answered with buttons
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
        """The steps of the conversation, in the order that they are asked."""
        return []

    async def save_command_name(self, update: Update, context: CallbackContext) -> int:
        """Start the conversation, remembering which command started it.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step of the conversation.
        """
        await self.log_command_execution(update, self.command_name)
        self.add_context_value(context, Context.COMMAND, self.command_name)
        return await self.states_methods[0](update, context)


class SelectProject(BaseConversation, ProjectMixin):
    """Conversation that chooses the project that the chat will work with.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
    """

    help = "Select one project to be used in next commands"
    section = Section.PROJECTS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """The steps of the conversation, in the order that they are asked."""
        return [self.ask_for_project, self.save_project]


class BaseConversationFromProject(BaseConversation, ProjectMixin):
    """Base conversation about something that belongs to a project."""

    async def ask_for_project(self, update: Update, context: CallbackContext) -> int:
        """Ask which project the conversation is about, if it isn't known yet.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step of the conversation, which is the one after choosing a
            project when the chat already chose one before.
        """
        return (
            await super().ask_for_project(update, context)
            if not self.get_context_value(context, Context.PROJECT)
            else await self.go_to_next_state(
                update, context, self.get_next_state(self.save_project), invoke_next_state=True
            )
        )


class NewTarget(BaseConversationFromProject, TargetMixin):
    """Conversation that creates a target in a project.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
    """

    help = "Create new target"
    section = Section.TARGETS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """The steps of the conversation, in the order that they are asked."""
        return [self.ask_for_project, self.save_project, self.ask_for_new_target, self.create_target]


class NewPort(BaseConversationFromProject, TargetMixin, TargetPortMixin, AuthenticationMixin):
    """Conversation that adds a port to a target, with its authentication.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
    """

    help = "Create new target port"
    section = Section.TARGETS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """The steps of the conversation, in the order that they are asked."""
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
    """Conversation that runs one tool against a target.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
    """

    help = "Execute a tool"
    section = Section.TASKS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """The steps of the conversation, in the order that they are asked."""
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
    """Conversation that runs a whole process against a target.

    Attributes:
        help: Description of the command.
        section: Group of the help message that the command belongs to.
    """

    help = "Execute a process"
    section = Section.TASKS

    @cached_property
    def states_methods(self) -> list[Callable]:
        """The steps of the conversation, in the order that they are asked."""
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

"""Options that organize the bot commands and their conversations."""

from enum import Enum


class Section(Enum):
    """Group of bot commands, used to organize the help message."""

    BASIC = "Basic"
    PROJECTS = "Projects"
    TARGETS = "Targets"
    TASKS = "Tasks"


class Context(Enum):
    """Data that a conversation remembers while it asks its questions.

    The project is the only one that survives a conversation, so the users don't
    have to choose it again for every command that they run.
    """

    COMMAND = "command"
    PROJECT = "project"
    TARGET = "target"
    TARGET_PORT = "target_port"
    AUTHENTICATION_TYPE = "authentication_type"
    AUTHENTICATION = "authentication"
    TOOL = "tool"
    CONFIGURATION = "configuration"
    PROCESS = "process"
    INTENSITY = "intensity"
    WORDLIST = "wordlist"
    INPUT_TECHNOLOGY = "input_technology"
    INPUT_VULNERABILITY = "input_vulnerability"

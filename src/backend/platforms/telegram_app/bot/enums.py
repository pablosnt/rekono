"""Enumeration classes for Telegram Bot command organization and context management.

Defines enums for categorizing bot commands and managing conversation context
data throughout multi-step security testing workflows.
"""

from enum import Enum


class Section(Enum):
    """Enumeration of bot command sections for organization and help display.

    Categorizes bot commands into logical sections for better organization
    in help messages and command discovery.

    Attributes:
        BASIC (str): Basic commands for authentication and help.
        SELECTION (str): Commands for selecting projects and contexts.
        TARGETS (str): Commands for target and port management.
        TASKS (str): Commands for executing tools and processes.
    """

    BASIC = "Basic"
    SELECTION = "Selection"
    TARGETS = "Targets"
    TASKS = "Tasks"


class Context(Enum):
    """Enumeration of conversation context keys for data persistence.

    Defines keys used to store and retrieve data across conversation states
    in multi-step security testing workflows.

    Attributes:
        COMMAND (str): Current command name context key.
        PROJECT (str): Selected project context key.
        TARGET (str): Selected target context key.
        TARGET_PORT (str): Selected target port context key.
        AUTHENTICATION_TYPE (str): Authentication type selection context key.
        AUTHENTICATION (str): Authentication configuration context key.
        TOOL (str): Selected security tool context key.
        CONFIGURATION (str): Tool configuration context key.
        PROCESS (str): Selected security process context key.
        INTENSITY (str): Execution intensity setting context key.
        WORDLIST (str): Selected wordlist context key.
        INPUT_TECHNOLOGY (str): Input technology parameter context key.
        INPUT_VULNERABILITY (str): Input vulnerability parameter context key.
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

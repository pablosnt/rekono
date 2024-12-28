from enum import Enum


class Section(Enum):
    BASIC = "Basic"
    SELECTION = "Selection"
    TARGETS = "Targets"
    TASKS = "Tasks"


class Context(Enum):
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

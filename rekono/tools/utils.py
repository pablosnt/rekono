import importlib

from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from resources.models import Wordlist
from targets.models import Target, TargetEndpoint, TargetPort
from tools.enums import FindingType


def get_tool_class_by_name(name):
    try:
        tools_module = importlib.import_module(
            f'tools.tools.{name.lower()}'
        )
        tool_class = name[0].upper() + name[1:].lower() + 'Tool'
        tool_class = getattr(tools_module, tool_class)
    except (AttributeError, ModuleNotFoundError):
        tools_module = importlib.import_module('tools.tools.base_tool')
        tool_class = getattr(tools_module, 'BaseTool')
    return tool_class


def get_finding_class_by_input_type(type):
    mapper = {
        FindingType.OSINT: [OSINT],
        FindingType.HOST: [Host, Target],
        FindingType.ENUMERATION: [Enumeration, TargetPort],
        FindingType.ENDPOINT: [Endpoint, TargetEndpoint],
        FindingType.TECHNOLOGY: [Technology],
        FindingType.VULNERABILITY: [Vulnerability],
        FindingType.CREDENTIAL: [Credential],
        FindingType.EXPLOIT: [Exploit],
        FindingType.WORDLIST: [Wordlist],
    }
    return mapper[type]


def get_relations_between_input_types() -> dict:
    return {
        FindingType.OSINT: [],
        FindingType.HOST: [],
        FindingType.ENUMERATION: [FindingType.HOST],
        FindingType.ENDPOINT: [FindingType.ENUMERATION],
        FindingType.TECHNOLOGY: [FindingType.ENUMERATION],
        FindingType.VULNERABILITY: [FindingType.TECHNOLOGY, FindingType.ENUMERATION],
        FindingType.CREDENTIAL: [],
        FindingType.EXPLOIT: [FindingType.TECHNOLOGY, FindingType.VULNERABILITY],
        FindingType.WORDLIST: [],
    }

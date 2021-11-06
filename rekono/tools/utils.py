import importlib

from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from resources.models import Wordlist
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


def get_finding_class_by_type(type):
    mapper = {
        FindingType.OSINT: OSINT,
        FindingType.HOST: Host,
        FindingType.ENUMERATION: Enumeration,
        FindingType.ENDPOINT: Endpoint,
        FindingType.TECHNOLOGY: Technology,
        FindingType.VULNERABILITY: Vulnerability,
        FindingType.CREDENTIAL: Credential,
        FindingType.EXPLOIT: Exploit,
        FindingType.WORDLIST: Wordlist,
    }
    return mapper[type]


def get_keys_from_argument(argument: str) -> list:
    if '{' in argument and '}' in argument:
        aux = argument.split('{')
        return [k.split('}')[0] for k in aux if '}' in k]
    return []

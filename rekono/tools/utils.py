import importlib

from tasks.models import Parameter
from findings.models import (OSINT, Enumeration, Exploit, Host, HttpEndpoint,
                             Technology, Vulnerability)
from projects.models import Target
from tools.arguments import checker
from tools.arguments.url import Url
from tools.models import Input
from tools.enums import FindingType


def get_tool_class_by_name(name):
    try:
        tools_module = importlib.import_module(
            f'tools.tools.{name}'
        )
        tool_class = name[0].upper() + name[1:] + 'Tool'
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
        FindingType.URL: Url,
        FindingType.HTTP_ENDPOINT: HttpEndpoint,
        FindingType.TECHNOLOGY: Technology,
        FindingType.VULNERABILITY: Vulnerability,
        FindingType.EXPLOIT: Exploit,
        FindingType.PARAMETER: Parameter
    }
    return mapper[type]


def get_keys_from_argument(argument: str) -> list:
    if '{' in argument and '}' in argument:
        aux = argument.split('{')
        return [k.split('}')[0] for k in aux if '}' in k]
    return []


def get_url_from_params(input: Input, target: Target, target_ports: list, findings: list) -> Url:
    enumeration_found = False
    for finding in findings:
        if isinstance(finding, Enumeration):
            enumeration_found = True
            if checker.check_input_condition(input, finding):
                url = Url(target, finding)
                if url.value:
                    return url
    if not enumeration_found:
        for p in target_ports:
            url = Url(target, p)
            if url.value:
                return url
        url = Url(target, None)
        if url.value:
            return url

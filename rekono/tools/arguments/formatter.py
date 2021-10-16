from findings.models import (OSINT, Enumeration, Exploit, Host, HttpEndpoint,
                             Technology, Vulnerability)
from tools.arguments import parser
from tools.arguments.constants import PORTS, PORTS_COMMAS, TARGET
from tools.arguments.url import Url


def argument_with_target(argument, target) -> str:
    data = {
        TARGET: target
    }
    return argument.format(**data)


def argument_with_target_ports(argument, target_ports) -> str:
    data = {
        PORTS: [tp.port for tp in target_ports],
        PORTS_COMMAS: ','.join([str(tp.port) for tp in target_ports])
    }
    return argument.format(**data)


def argument_with_finding(argument, finding) -> str:
    parsers = {
        OSINT: parser.osint,
        Host: parser.host,
        Enumeration: parser.enumeration,
        HttpEndpoint: parser.http_endpoint,
        Technology: parser.technology,
        Vulnerability: parser.vulnerability,
        Exploit: parser.exploit,
        Url: parser.url,
    }
    data = parsers[finding.__class__](finding)
    return argument.format(**data)


def argument_with_findings(argument, findings) -> str:
    parsers = {
        Enumeration: parser.enumeration
    }
    data = {}
    for result in findings:
        data = parsers[result.__class__](result, data)
    return argument.format(**data)


def argument_with_parameter(argument, parameter) -> str:
    data = parser.parameter(parameter)
    return argument.format(**data)


def argument_with_parameters(argument, parameters) -> str:
    data = {}
    for parameter in parameters:
        data = parser.parameter_multiple(parameter, data)
    return argument.format(**data)

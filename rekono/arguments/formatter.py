from arguments import parser
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from targets.models import Target


def argument_with_one(argument, finding) -> str:
    parsers = {
        Target: parser.target,
        OSINT: parser.osint,
        Host: parser.host,
        Enumeration: parser.enumeration,
        Endpoint: parser.endpoint,
        Technology: parser.technology,
        Vulnerability: parser.vulnerability,
        Credential: parser.credential,
        Exploit: parser.exploit,
    }
    data = parsers[finding.__class__](finding)
    return format_argument(argument, data)


def argument_with_multiple(argument, findings) -> str:
    parsers = {
        Enumeration: parser.enumeration,
    }
    data = {}
    for result in findings:
        data = parsers[result.__class__](result, data)
    return format_argument(argument, data)


def argument_with_target_ports(argument, target_ports, target) -> str:
    data = parser.target_port(target_ports, target)
    return format_argument(argument, data)


def format_argument(argument, data):
    cleaned = {}
    for key, value in data.items():
        if value:
            cleaned[key] = value
    return argument.format(**cleaned)

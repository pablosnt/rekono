from arguments import parser
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from resources.models import Wordlist
from targets.models import Target, TargetPort


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
        Wordlist: parser.wordlist,
    }
    data = parsers[finding.__class__](finding)
    return format_argument(argument, data)


def argument_with_multiple(argument, findings) -> str:
    parsers = {
        Enumeration: parser.enumeration,
        TargetPort: parser.target_port,
    }
    data = {}
    for result in findings:
        data = parsers[result.__class__](result, data)
    return format_argument(argument, data)


def format_argument(argument, data):
    cleaned = {}
    for key, value in data.items():
        if value:
            cleaned[key] = value
    return argument.format(**cleaned)

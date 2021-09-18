from typing import Any

from executions.enums import ParameterKey
from findings.models import Enumeration, Host, HttpEndpoint, Vulnerability
from projects.models import Target
from tools.models import Input
from projects import utils


def check_parameter(parameter) -> None:
    checkers = {
        ParameterKey.TECHNOLOGY: '',
        ParameterKey.VERSION: '',
        ParameterKey.HTTP_ENDPOINT: '',
        ParameterKey.CVE: '',
        ParameterKey.EXPLOIT: '',
        ParameterKey.WORDLIST: '',
    }
    checkers[parameter.key]
    return parameter.value


def check_input_condition(input: Input, finding: Any) -> bool:
    checkers = {
        Target: check_target,
        Host: check_host,
        Enumeration: check_enumeration,
        HttpEndpoint: check_http_endpoint,
        Vulnerability: check_vulnerability
    }
    if finding.__class__ in checkers and input.filters:
        return checkers[finding.__class__](input, finding)
    else:
        return True


def check_target(input: Input, target: Target) -> bool:
    try:
        to_check = int(input.filter)
        return Target.TargetType(to_check) == target.type
    except ValueError:
        return Target.TargetType[input.filter.upper()] == target.type


def check_host(input: Input, host: Host) -> bool:
    try:
        to_check = int(input.filter)
        return Target.TargetType(to_check) == utils.get_target_type(host.address)
    except ValueError:
        return Target.TargetType[input.filter.upper()] == utils.get_target_type(host.address)


def check_enumeration(input: Input, enumeration: Enumeration) -> bool:
    try:
        to_check = int(input.filter)
        return to_check == enumeration.port
    except ValueError:
        return input.filter in enumeration.service


def check_http_endpoint(input: Input, http_endpoint: HttpEndpoint) -> bool:
    try:
        status_code = int(input.filter)
        return status_code == http_endpoint.status
    except ValueError:
        return http_endpoint.endpoint.startswith(input.filter)


def check_vulnerability(input: Input, vulnerability: Vulnerability) -> bool:
    return (input.filter.lower() == 'cve' and vulnerability.cve)

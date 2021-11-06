from typing import Any

from findings.models import Endpoint, Enumeration, Host, Vulnerability
from targets import utils
from targets.enums import TargetType
from targets.models import Target
from tools.models import Input


def check_input_condition(input: Input, finding: Any) -> bool:
    checkers = {
        Target: check_target,
        Host: check_host,
        Enumeration: check_enumeration,
        Endpoint: check_endpoint,
        Vulnerability: check_vulnerability
    }
    if finding.__class__ in checkers and input.filter:
        return checkers[finding.__class__](input, finding)
    else:
        return True


def check_target(input: Input, target: Target) -> bool:
    try:
        to_check = int(input.filter)
        return TargetType(to_check) == target.type
    except ValueError:
        return TargetType[input.filter.upper()] == target.type


def check_host(input: Input, host: Host) -> bool:
    try:
        to_check = int(input.filter)
        return TargetType(to_check) == utils.get_target_type(host.address)
    except ValueError:
        return TargetType[input.filter.upper()] == utils.get_target_type(host.address)


def check_enumeration(input: Input, enumeration: Enumeration) -> bool:
    try:
        to_check = int(input.filter)
        return to_check == enumeration.port
    except ValueError:
        return input.filter in enumeration.service


def check_endpoint(input: Input, endpoint: Endpoint) -> bool:
    try:
        status_code = int(input.filter)
        return status_code == endpoint.status
    except ValueError:
        return (
            endpoint.endpoint.startswith(input.filter)
            or (endpoint.enumeration and input.filter in endpoint.enumeration.service)
        )


def check_vulnerability(input: Input, vulnerability: Vulnerability) -> bool:
    return (input.filter.lower() == 'cve' and vulnerability.cve)

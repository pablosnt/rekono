import os
import re
from typing import Any

from arguments.constants import (CVE_REGEX, DIGITS_REGEX, ENDPOINT_REGEX,
                                 TECHNOLOGY_REGEX, WORDLIST_FILE_REGEX,
                                 WORDLIST_PATH_REGEX)
from findings.models import Endpoint, Enumeration, Host, Vulnerability
from targets import utils
from targets.enums import TargetType
from targets.models import Target
from tasks.enums import ParameterKey
from tools.exceptions import InvalidParameterException
from tools.models import Input


def check_parameter(parameter) -> None:
    checkers = {
        ParameterKey.TECHNOLOGY: check_technology_param,
        ParameterKey.VERSION: check_version_param,
        ParameterKey.ENDPOINT: check_endpoint_param,
        ParameterKey.CVE: check_cve_param,
        ParameterKey.EXPLOIT: check_exploit_param,
        ParameterKey.WORDLIST: check_wordlist_param,
    }
    if not checkers[parameter.key](parameter.value):
        raise InvalidParameterException(f'Invalid value for {parameter.key} parameter')


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


def check_technology_param(technology: str) -> bool:
    return bool(re.fullmatch(TECHNOLOGY_REGEX, technology))


def check_version_param(version: str) -> bool:
    return (
        bool(re.fullmatch(TECHNOLOGY_REGEX, version))
        and bool(re.findall(DIGITS_REGEX, version))
        and '.' in version
    )


def check_endpoint_param(endpoint: str) -> bool:
    return bool(re.fullmatch(ENDPOINT_REGEX, endpoint))


def check_cve_param(cve: str) -> bool:
    return bool(re.fullmatch(CVE_REGEX, cve))


def check_exploit_param(exploit: str) -> bool:
    # TODO: To implement after add some exploitation tool
    return True


def check_wordlist_param(wordlist: str) -> bool:
    check = os.path.isfile(wordlist)
    directory = os.path.dirname(os.path.abspath(wordlist))
    check = check and bool(re.fullmatch(WORDLIST_PATH_REGEX, directory))
    filename = os.path.basename(wordlist)
    check = check and bool(re.fullmatch(WORDLIST_FILE_REGEX, filename))
    return check

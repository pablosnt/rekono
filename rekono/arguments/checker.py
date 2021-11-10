import os
from typing import Any

from findings.enums import Severity
from findings.models import (Endpoint, Enumeration, Host, Technology,
                             Vulnerability)
from resources.models import Wordlist
from security import file_upload
from targets import utils
from targets.enums import TargetType
from targets.models import Target
from tools.models import Input


def check_finding(input: Input, finding: Any) -> bool:
    checkers = {
        Target: check_target,                   # By TargetType
        Host: check_host,                       # By TargetType
        Enumeration: check_enumeration,         # By Port or Service contains
        Endpoint: check_endpoint,               # By StatusCode or Endpoint startswith
        Technology: check_technology,           # By Name
        Vulnerability: check_vulnerability,     # By Severity, CVE exists, exact CVE or exact CWE
        Wordlist: check_wordlist,               # Check file checksum
    }
    if finding.__class__ in checkers and input.filter:
        return checkers[finding.__class__](input, finding)
    else:
        return True


def check_target(input: Input, target: Target) -> bool:
    try:
        return TargetType(input.filter) == target.type
    except ValueError:
        return True


def check_host(input: Input, host: Host) -> bool:
    try:
        return TargetType(input.filter) == utils.get_target_type(host.address)
    except ValueError:
        return True


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
        return endpoint.endpoint.startswith(input.filter)


def check_technology(input: Input, technology: Technology) -> bool:
    return input.filter in technology.name


def check_vulnerability(input: Input, vulnerability: Vulnerability) -> bool:
    try:
        return Severity(input.filter) == vulnerability.severity
    except ValueError:
        f = input.filter.lower()
        return (
            f == 'cve' and vulnerability.cve
            or (f.startswith('cve-') and f == vulnerability.cve.lower())
            or (f.startswith('cwe-') and f == vulnerability.cwe.lower())
        )


def check_wordlist(input: Input, wordlist: Wordlist) -> bool:
    exist = os.path.isfile(wordlist.path)
    if exist and wordlist.checksum:
        return file_upload.check_checksum(wordlist.path, wordlist.checksum)
    return exist

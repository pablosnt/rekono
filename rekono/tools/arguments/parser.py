from executions.enums import ParameterKey
from findings.models import (OSINT, Enumeration, Exploit, Host, HttpEndpoint,
                            Technology, Vulnerability)
from tools.arguments.constants import PORTS, PORTS_COMMAS, TARGET, PORT


def osint(osint: OSINT) -> dict:
    if osint.data_type in [OSINT.DataType.IP, OSINT.DataType.DOMAIN]:
        return {
            TARGET: osint.data,
        }
    return {}


def host(host: Host) -> dict:
    return {
        TARGET: host.address
    }


def enumeration(
    enumeration: Enumeration,
    accumulated: dict = {}
) -> dict:
    output = {
        TARGET: enumeration.host.address,
        PORT: enumeration.port,
        PORTS: [enumeration.port]
    }
    if accumulated and PORTS in accumulated:
        output[PORTS] = accumulated[PORTS]
        output[PORTS].append(enumeration.port)
    output[PORTS_COMMAS] = ','.join([str(port) for port in output[PORTS]])
    return output


def http_endpoint(http_endpoint):
    output = enumeration(http_endpoint.enumeration)
    output[ParameterKey.HTTP_ENDPOINT.name.lower()] = http_endpoint.endpoint
    return output


def technology(technology: Technology) -> dict:
    output = enumeration(technology.enumeration)
    output[ParameterKey.TECHNOLOGY.name.lower()] = technology.name
    if technology.version:
        output[ParameterKey.VERSION.name.lower()] = technology.version
    return output


def vulnerability(vulnerability: Vulnerability) -> dict:
    output = {}
    if vulnerability.enumeration:
        output = enumeration(vulnerability.enumeration)
    elif vulnerability.technology:
        output = technology(vulnerability.technology)
    if vulnerability.cve:
        output[ParameterKey.CVE.name.lower()] = vulnerability.cve
    return output


def exploit(exploit: Exploit) -> dict:
    output = vulnerability(exploit.vulnerability)
    output[ParameterKey.EXPLOIT.name.lower()] = exploit.name
    return output

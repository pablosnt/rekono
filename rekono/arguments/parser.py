from arguments.enums import Keyword
from arguments.url import get_url
from findings.enums import DataType
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from resources.models import Wordlist
from targets.models import Target, TargetEndpoint, TargetPort


def target(target: Target) -> dict:
    return {
        Keyword.TARGET.name.lower(): target.target,
        Keyword.HOST.name.lower(): target.target,
        Keyword.URL.name.lower(): get_url(target.target)
    }


def target_port(target_port: TargetPort, accumulated: dict = {}) -> dict:
    output = {
        Keyword.TARGET.name.lower(): target_port.target.target,
        Keyword.HOST.name.lower(): target_port.target.target,
        Keyword.PORT.name.lower(): target_port.port,
        Keyword.PORTS.name.lower(): [target_port.port],
        Keyword.URL.name.lower(): get_url(target_port.target.target, target_port.port)
    }
    if accumulated and Keyword.PORTS.name.lower() in accumulated:
        output[Keyword.PORTS.name.lower()] = accumulated[Keyword.PORTS.name.lower()]
        output[Keyword.PORTS.name.lower()].append(target_port.port)
    output[Keyword.PORTS_COMMAS.name.lower()] = ','.join([str(port) for port in output[Keyword.PORTS.name.lower()]])    # noqa: E501
    return output


def target_endpoints(target_endpoint: TargetEndpoint) -> dict:
    output = target_port([target_endpoint.target_port])
    output[Keyword.URL.name.lower()] = get_url(
        target_endpoint.target_port.target.target,
        target_endpoint.target_port.port,
        target_endpoint.endpoint
    )
    output[Keyword.ENDPOINT.name.lower()] = target_endpoint.endpoint
    return output


def osint(osint: OSINT) -> dict:
    if osint.data_type in [DataType.IP, DataType.DOMAIN]:
        return {
            Keyword.TARGET.name.lower(): osint.data,
            Keyword.HOST.name.lower(): osint.data,
            Keyword.URL.name.lower(): get_url(osint.data)
        }
    return {}


def host(host: Host) -> dict:
    return {
        Keyword.TARGET.name.lower(): host.address,
        Keyword.HOST.name.lower(): host.address,
        Keyword.URL.name.lower(): get_url(host.address),
    }


def enumeration(enumeration: Enumeration, accumulated: dict = {}) -> dict:
    output = {
        Keyword.TARGET.name.lower(): f'{enumeration.host.address}:{enumeration.port}',
        Keyword.HOST.name.lower(): enumeration.host.address,
        Keyword.PORT.name.lower(): enumeration.port,
        Keyword.PORTS.name.lower(): [enumeration.port],
        Keyword.URL.name.lower(): get_url(enumeration.host.address, enumeration.port),
    }
    if accumulated and Keyword.PORTS.name.lower() in accumulated:
        output[Keyword.PORTS.name.lower()] = accumulated[Keyword.PORTS.name.lower()]
        output[Keyword.PORTS.name.lower()].append(enumeration.port)
    output[Keyword.PORTS_COMMAS.name.lower()] = ','.join([str(port) for port in output[Keyword.PORTS.name.lower()]])    # noqa: E501
    return output


def endpoint(endpoint: Endpoint):
    output = enumeration(endpoint.enumeration)
    output[Keyword.URL.name.lower()] = get_url(
        endpoint.enumeration.host.address,
        endpoint.enumeration.port,
        endpoint.endpoint
    )
    output[Keyword.ENDPOINT.name.lower()] = endpoint.endpoint
    return output


def technology(technology: Technology) -> dict:
    output = enumeration(technology.enumeration)
    output[Keyword.TECHNOLOGY.name.lower()] = technology.name
    if technology.version:
        output[Keyword.VERSION.name.lower()] = technology.version
    return output


def vulnerability(vulnerability: Vulnerability) -> dict:
    output = {}
    if vulnerability.enumeration:
        output = enumeration(vulnerability.enumeration)
    elif vulnerability.technology:
        output = technology(vulnerability.technology)
    if vulnerability.cve:
        output[Keyword.CVE.name.lower()] = vulnerability.cve
    return output


def credential(credential: Credential) -> dict:
    return {
        Keyword.EMAIL.name.lower(): credential.email,
        Keyword.USERNAME.name.lower(): credential.username,
        Keyword.SECRET.name.lower(): credential.secret,
    }


def exploit(exploit: Exploit) -> dict:
    output = vulnerability(exploit.vulnerability)
    output[Keyword.EXPLOIT.name.lower()] = exploit.name
    return output


def wordlist(wordlist: Wordlist) -> dict:
    return {
        Keyword.WORDLIST.name.lower(): wordlist.path
    }

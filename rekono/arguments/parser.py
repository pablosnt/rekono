from arguments.enums import Keyword
from arguments.url import get_url
from findings.enums import DataType
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from resources.models import Wordlist
from targets.models import Target


def target(target: Target) -> dict:
    return {
        Keyword.TARGET.name.lower(): target.target,
        Keyword.HOST.name.lower(): target.target,
        Keyword.URL.name.lower(): get_url(target.target, None)
    }


def target_port(target_ports: list, target: Target) -> dict:
    urls = [get_url(target.target, tp) for tp in target_ports]
    urls = [url for url in urls if url]
    return {
        Keyword.PORT.name.lower(): target_ports[0].port,
        Keyword.PORTS.name.lower(): [tp.port for tp in target_ports],
        Keyword.PORTS_COMMAS.name.lower(): ','.join([str(tp.port) for tp in target_ports]),
        Keyword.URL.name.lower(): urls[0] if urls else None,
    }


def osint(osint: OSINT) -> dict:
    if osint.data_type in [DataType.IP, DataType.DOMAIN]:
        return {
            Keyword.TARGET.name.lower(): osint.data,
            Keyword.HOST.name.lower(): osint.data,
            Keyword.URL.name.lower(): get_url(osint.data, None)
        }
    return {}


def host(host: Host) -> dict:
    return {
        Keyword.TARGET.name.lower(): host.address,
        Keyword.HOST.name.lower(): host.address,
        Keyword.URL.name.lower(): get_url(host.address, None),
    }


def enumeration(enumeration: Enumeration, accumulated: dict = {}) -> dict:
    output = {
        Keyword.TARGET.name.lower(): f'{enumeration.host.address}:{enumeration.port}',
        Keyword.HOST.name.lower(): enumeration.host.address,
        Keyword.PORT.name.lower(): enumeration.port,
        Keyword.PORTS.name.lower(): [enumeration.port],
        Keyword.URL.name.lower(): get_url(None, enumeration),
    }
    if accumulated and Keyword.PORTS.name.lower() in accumulated:
        output[Keyword.PORTS.name.lower()] = accumulated[Keyword.PORTS.name.lower()]
        output[Keyword.PORTS.name.lower()].append(enumeration.port)
    output[Keyword.PORTS_COMMAS.name.lower()] = ','.join([str(port) for port in output[Keyword.PORTS.name.lower()]])    # noqa: E501
    return output


def endpoint(endpoint: Endpoint):
    output = enumeration(endpoint.enumeration)
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
        Keyword.WORDLIST: wordlist.path
    }

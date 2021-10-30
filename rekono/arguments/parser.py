from arguments import checker
from arguments.constants import (EMAIL, HOST, PORT, PORTS, PORTS_COMMAS,
                                 SECRET, TARGET, URL, USERNAME)
from arguments.url import get_url
from findings.enums import DataType
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from targets.models import Target
from tasks.enums import ParameterKey
from tasks.models import Parameter


def target(target: Target) -> dict:
    return {
        TARGET: target.target,
        HOST: target.target,
        URL: get_url(target.target, None)
    }


def target_port(target_ports: list, target: Target) -> dict:
    urls = [get_url(target.target, tp) for tp in target_ports]
    urls = [url for url in urls if url]
    return {
        PORT: target_ports[0].port,
        PORTS: [tp.port for tp in target_ports],
        PORTS_COMMAS: ','.join([str(tp.port) for tp in target_ports]),
        URL: urls[0] if urls else None,
    }


def osint(osint: OSINT) -> dict:
    if osint.data_type in [DataType.IP, DataType.DOMAIN]:
        return {
            TARGET: osint.data,
            HOST: osint.data,
            URL: get_url(osint.data, None)
        }
    return {}


def host(host: Host) -> dict:
    return {
        TARGET: host.address,
        HOST: host.address,
        URL: get_url(host.address, None),
    }


def enumeration(enumeration: Enumeration, accumulated: dict = {}) -> dict:
    output = {
        TARGET: f'{enumeration.host.address}:{enumeration.port}',
        HOST: enumeration.host.address,
        PORT: enumeration.port,
        PORTS: [enumeration.port],
        URL: get_url(None, enumeration),
    }
    if accumulated and PORTS in accumulated:
        output[PORTS] = accumulated[PORTS]
        output[PORTS].append(enumeration.port)
    output[PORTS_COMMAS] = ','.join([str(port) for port in output[PORTS]])
    return output


def endpoint(endpoint: Endpoint):
    output = enumeration(endpoint.enumeration)
    output[ParameterKey.ENDPOINT.name.lower()] = endpoint.endpoint
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


def credential(credential: Credential) -> dict:
    return {
        EMAIL: credential.email,
        USERNAME: credential.username,
        SECRET: credential.secret,
    }


def exploit(exploit: Exploit) -> dict:
    output = vulnerability(exploit.vulnerability)
    output[ParameterKey.EXPLOIT.name.lower()] = exploit.name
    return output


def parameter(parameter: Parameter) -> dict:
    checker.check_parameter(parameter)
    return {
        ParameterKey(parameter.key).name.lower(): parameter.value
    }


def parameter_multiple(parameter: Parameter, accumulated: dict = {}) -> dict:
    checker.check_parameter(parameter)
    output = {
        ParameterKey(parameter.key).name.lower() + '_data': [parameter.value],
        ParameterKey(parameter.key).name.lower(): parameter.value
    }
    if accumulated:
        aux = accumulated[ParameterKey(parameter.key).name.lower() + '_data']
        aux.append(parameter.value)
        output = {
            ParameterKey(parameter.key).name.lower(): ','.join(aux)
        }
    return output

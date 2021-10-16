import ipaddress
import socket
import re

from targets.exceptions import InvalidTargetException
from targets.models import Target
from targets.enums import TargetType


IP_NETWORK_REGEX = '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/[0-9]{1,2}'
IP_RANGE_REGEX = '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}-[0-9]{1,3}'


def get_target_type(target: str) -> TargetType:
    try:
        ip = ipaddress.ip_address(target)
        if ip.is_private:
            return TargetType.PRIVATE_IP
        else:
            return TargetType.PUBLIC_IP
    except ValueError:
        pass
    try:
        ipaddress.ip_network(target)
        return TargetType.NETWORK
    except ValueError:
        pass
    if bool(re.fullmatch(IP_NETWORK_REGEX, target)):
        return TargetType.NETWORK
    if bool(re.fullmatch(IP_RANGE_REGEX, target)):
        return TargetType.IP_RANGE
    try:
        socket.gethostbyname(target)
        return TargetType.DOMAIN
    except socket.gaierror:
        pass
    raise InvalidTargetException(
        f'Invalid target {target}. IP address, IP range or domain is required'
    )

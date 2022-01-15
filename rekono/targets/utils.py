import ipaddress
import re
import socket

from targets.enums import TargetType
from targets.exceptions import InvalidTargetException

IP_RANGE_REGEX = '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}-[0-9]{1,3}'


def get_target_type(target: str) -> str:
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
    if bool(re.fullmatch(IP_RANGE_REGEX, target)):
        return TargetType.IP_RANGE
    try:
        socket.gethostbyname(target)
        return TargetType.DOMAIN
    except socket.gaierror:
        pass
    raise InvalidTargetException(f'Invalid target {target}. IP address, IP range or domain is required')

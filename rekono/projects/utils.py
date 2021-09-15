import ipaddress
import socket

from projects.exceptions import InvalidTargetException
from projects.models import Target


def get_target_type(target: str) -> Target.TargetType:
    try:
        ip = ipaddress.ip_address(target)
        if ip.is_private:
            return Target.TargetType.PRIVATE_IP
        else:
            return Target.TargetType.PUBLIC_IP
    except ValueError:
        pass
    try:
        ipaddress.ip_network(target)
        return Target.TargetType.NETWORK
    except ValueError:
        pass
    try:
        socket.gethostbyname(target)
        return Target.TargetType.DOMAIN
    except socket.gaierror:
        pass
    raise InvalidTargetException(
        f'Invalid target {target}. IP address, IP range or domain is required'
    )

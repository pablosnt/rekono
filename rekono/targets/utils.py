import ipaddress
import logging
import re
import socket

from django.core.exceptions import ValidationError
from security.input_validation import IP_RANGE_REGEX

from targets.enums import TargetType

logger = logging.getLogger()                                                    # Rekono logger


def get_target_type(target: str) -> str:
    '''Get target type from target address.

    Args:
        target (str): Target value

    Raises:
        ValidationError: Raised if target doesn't match any supported type

    Returns:
        str: Target type associated to the target
    '''
    if target in [
        '127.0.0.1', 'localhost', 'frontend', 'backend',
        'postgres', 'redis', 'postfix', 'initialize',
        'tasks-worker', 'executions-worker', 'findings-worker',
        'emails-worker', 'telegram-bot', 'nginx'
    ]:
        # Target is invalid
        raise ValidationError({'target': f'Invalid target {target}'})
    try:
        # Check if target is an IP address (IPv4 or IPv6)
        ip = ipaddress.ip_address(target)
        if ip.is_private:                                                       # Private IP (also for IPv6)
            return TargetType.PRIVATE_IP
        else:                                                                   # Public IP (also for IPv4)
            return TargetType.PUBLIC_IP
    except ValueError:
        pass                                                                    # Target is not an IP address
    try:
        ipaddress.ip_network(target)                                            # Check if target is a network
        return TargetType.NETWORK
    except ValueError:
        pass                                                                    # Target is not a network
    if bool(re.fullmatch(IP_RANGE_REGEX, target)):                              # Check if target is an IP range
        return TargetType.IP_RANGE
    try:
        socket.gethostbyname(target)                                            # Check if target is a Domain
        return TargetType.DOMAIN
    except socket.gaierror:
        pass
    logger.warning(f'[Security] Invalid target {target}')
    # Target is invalid or target type is not supported
    raise ValidationError({'target': f'Invalid target {target}. IP address, IP range or domain is required'})

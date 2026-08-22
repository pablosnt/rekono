"""Types of targets that Rekono can scan."""

from django.db import models
from django.db.models.enums import Choices


class TargetType(models.TextChoices):
    """Kind of host, or group of hosts, that a target identifies.

    The type decides which tools can scan a target, since the ones that only accept
    one host can't run against a network or an IP range.

    Attributes:
        PRIVATE_IP: IP address, IPv4 or IPv6, reserved for private networks.
        PUBLIC_IP: IP address, IPv4 or IPv6, routable on the Internet.
        NETWORK: Network in CIDR notation, like 192.168.1.0/24.
        IP_RANGE: Range of addresses, like 192.168.1.1-100.
        DOMAIN: Domain name that resolves to an IP address.
    """

    PRIVATE_IP = "Private IP"
    PUBLIC_IP = "Public IP"
    NETWORK = "Network"
    IP_RANGE = "IP range"
    DOMAIN = "Domain"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
TargetType: type[Choices] = TargetType

"""Enums for target classification and management.

Defines enumeration classes for target types and configuration options
used throughout the targets system.
"""

from django.db import models
from django.db.models.enums import Choices


class TargetType(models.TextChoices):
    """Enumeration of supported target types.

    Defines the types of targets that can be specified for security testing
    operations, including various IP formats, networks, and domain names.

    Attributes:
        PRIVATE_IP (str): RFC 1918 private IP addresses (IPv4/IPv6)
        PUBLIC_IP (str): Internet-routable IP addresses (IPv4/IPv6)
        NETWORK (str): CIDR notation networks (e.g., 192.168.1.0/24)
        IP_RANGE (str): Hyphen-separated IP ranges (e.g., 192.168.1.1-100)
        DOMAIN (str): DNS-resolvable domain names and hostnames
    """

    PRIVATE_IP = "Private IP"
    PUBLIC_IP = "Public IP"
    NETWORK = "Network"
    IP_RANGE = "IP range"
    DOMAIN = "Domain"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
TargetType: type[Choices] = TargetType

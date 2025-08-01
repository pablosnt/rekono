"""Enums for findings module.

This module contains the enums used to categorize and prioritize security
findings discovered during security assessments. It includes severity levels,
OSINT data types, host operating systems, port statuses, protocols, path types,
and triage statuses.
"""

from typing import Any

from django.db import models
from django.db.models.enums import Choices


class Severity(models.IntegerChoices):
    """Severity levels for security findings.

    Represents the criticality of security findings from informational
    to critical, used for prioritization and reporting.
    """

    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    def __str__(self) -> Any:
        """Return the severity level as a string.

        Returns:
            str: The severity level as a string
        """
        return self.name.capitalize()


class OSINTDataType(models.TextChoices):
    """Types of OSINT (Open Source Intelligence) data.

    Defines the different categories of information that can be discovered
    through open source intelligence gathering techniques.
    """

    IP = "IP"
    DOMAIN = "Domain"
    VHOST = "VHOST"
    URL = "URL"
    EMAIL = "Email"
    ASN = "ASN"
    USER = "Username"
    PASSWORD = "Password"


class HostOS(models.TextChoices):
    """Operating system types for discovered hosts.

    Categorizes the operating system running on discovered hosts
    for better analysis and reporting.
    """

    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "MacOS"
    IOS = "iOS"
    ANDROID = "Android"
    SOLARIS = "Solaris"
    FREEBSD = "FreeBSD"
    OTHER = "Other"


class PortStatus(models.TextChoices):
    """Network port status values.

    Represents the state of network ports discovered during scanning,
    indicating whether they are open, closed, filtered, etc.
    """

    OPEN = "Open"
    OPEN_FILTERED = "Open - Filtered"
    FILTERED = "Filtered"
    CLOSED = "Closed"


class Protocol(models.TextChoices):
    """Network protocols.

    Defines the transport layer protocols used for network communication.
    """

    UDP = "UDP"
    TCP = "TCP"


class PathType(models.TextChoices):
    """Types of web paths or endpoints.

    Categorizes discovered web paths as either API endpoints or file shares
    for better organization and analysis.
    """

    ENDPOINT = "ENDPOINT"
    SHARE = "SHARE"


class TriageStatus(models.TextChoices):
    """Status values for finding triage process.

    Represents the current state of a finding in the triage workflow,
    indicating whether it has been reviewed and what action was taken.
    """

    FALSE_POSITIVE = "False Positive"
    TRUE_POSITIVE = "True Positive"
    WONT_FIX = "Won't Fix"
    UNTRIAGED = "Untriaged"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Severity: type[Choices] = Severity
OSINTDataType: type[Choices] = OSINTDataType
HostOS: type[Choices] = HostOS
PortStatus: type[Choices] = PortStatus
Protocol: type[Choices] = Protocol
TriageStatus: type[Choices] = TriageStatus

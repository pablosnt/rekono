"""Values that classify the findings: severity, status, data types, and triage."""

from django.db import models
from django.db.models.enums import Choices


class Severity(models.IntegerChoices):
    """Risk of a vulnerability, used to prioritize its remediation.

    The values are ordered from the lowest to the highest risk, so the findings can
    be filtered and sorted by how urgent they are.
    """

    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    def __str__(self) -> str:
        """Return the capitalized name of the severity."""
        return self.name.capitalize()


class OSINTDataType(models.TextChoices):
    """Kind of public information that an OSINT finding contains.

    Attributes:
        IP: IP address of the organization.
        DOMAIN: Domain name of the organization.
        VHOST: Virtual host served by one of its addresses.
        URL: URL exposed by the organization.
        EMAIL: Email address of the organization.
        ASN: Autonomous System Number assigned to it.
        USER: Username of one of its members.
        PASSWORD: Leaked password.
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
    """Operating system that a host runs, as the tools fingerprint it."""

    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "MacOS"
    IOS = "iOS"
    ANDROID = "Android"
    SOLARIS = "Solaris"
    FREEBSD = "FreeBSD"
    OTHER = "Other"


class PortStatus(models.TextChoices):
    """State of a port, as the port scanners report it.

    The filtered variants mean that the scanner couldn't tell the state apart from
    the answer of a firewall.
    """

    OPEN = "Open"
    OPEN_FILTERED = "Open - Filtered"
    FILTERED = "Filtered"
    CLOSED = "Closed"
    CLOSED_FILTERED = "Closed - Filtered"


class TransportProtocol(models.TextChoices):
    """Transport protocol of the service that listens in a port."""

    UDP = "UDP"
    TCP = "TCP"


class PathType(models.TextChoices):
    """Kind of resource that a path finding points to.

    Attributes:
        ENDPOINT: Path of a web application.
        SHARE: Directory shared by a file sharing service.
    """

    ENDPOINT = "Endpoint"
    SHARE = "Share"


class AutoFixedReason(models.TextChoices):
    """Why Rekono marked a finding as fixed without the user asking for it.

    Attributes:
        NO_LONGER_DETECTED: The same executions stopped reporting the finding.
        PARENT_FIXED: The finding where this one was found got fixed.
    """

    NO_LONGER_DETECTED = "No longer detected by same executions"
    PARENT_FIXED = "Parent finding got fixed"


class TriageStatus(models.TextChoices):
    """Conclusion of the review of a finding by an auditor.

    Attributes:
        FALSE_POSITIVE: The finding isn't real, so it's excluded from the reports.
        TRUE_POSITIVE: The finding is real and must be remediated.
        WONT_FIX: The finding is real, but it was accepted as a risk.
        UNTRIAGED: The finding hasn't been reviewed yet.
    """

    FALSE_POSITIVE = "False Positive"
    TRUE_POSITIVE = "True Positive"
    WONT_FIX = "Won't Fix"
    UNTRIAGED = "Untriaged"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
AutoFixedReason: type[Choices] = AutoFixedReason
Severity: type[Choices] = Severity
OSINTDataType: type[Choices] = OSINTDataType
HostOS: type[Choices] = HostOS
PortStatus: type[Choices] = PortStatus
TransportProtocol: type[Choices] = TransportProtocol
TriageStatus: type[Choices] = TriageStatus

"""Enumeration definitions for security findings categorization.

Provides enumeration classes for categorizing and prioritizing security findings
discovered during assessments, including severity levels, data types, status values,
and triage classifications.
"""

from django.db import models
from django.db.models.enums import Choices


class Severity(models.IntegerChoices):
    """Security finding severity levels for risk prioritization.

    Defines criticality levels from informational to critical for
    prioritizing security findings and generating reports.

    Attributes:
        INFO (int): Informational findings with no immediate security impact
        LOW (int): Low severity findings with minimal risk
        MEDIUM (int): Medium severity findings requiring attention
        HIGH (int): High severity findings requiring immediate attention
        CRITICAL (int): Critical severity findings requiring urgent response
    """

    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    def __str__(self) -> str:
        """Return the severity level as a string.

        Returns:
            str: Capitalized severity level name.
        """
        return self.name.capitalize()


class OSINTDataType(models.TextChoices):
    """Open Source Intelligence data type classifications.

    Categories of information discoverable through OSINT techniques
    including network identifiers, credentials, and organizational data.

    Attributes:
        IP (str): IP address identifiers
        DOMAIN (str): Domain name identifiers
        VHOST (str): Virtual host identifiers
        URL (str): URL resources and endpoints
        EMAIL (str): Email address identifiers
        ASN (str): Autonomous System Number identifiers
        USER (str): Username credentials
        PASSWORD (str): Password credentials
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
    """Host operating system type classifications.

    Categorizes operating systems running on discovered hosts
    for security analysis and reporting purposes.

    Attributes:
        LINUX (str): Linux-based operating systems
        WINDOWS (str): Microsoft Windows operating systems
        MACOS (str): Apple macOS operating systems
        IOS (str): Apple iOS mobile operating systems
        ANDROID (str): Google Android mobile operating systems
        SOLARIS (str): Oracle Solaris operating systems
        FREEBSD (str): FreeBSD operating systems
        OTHER (str): Other or unidentified operating systems
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
    """Network port scan status classifications.

    Defines the state of network ports discovered during scanning
    operations for service enumeration and security assessment.

    Attributes:
        OPEN (str): Port is open and accepting connections
        OPEN_FILTERED (str): Port appears open but may be filtered
        FILTERED (str): Port is filtered by firewall or security device
        CLOSED (str): Port is closed and not accepting connections
    """

    OPEN = "Open"
    OPEN_FILTERED = "Open - Filtered"
    FILTERED = "Filtered"
    CLOSED = "Closed"


class TransportProtocol(models.TextChoices):
    """Network transport layer protocol types.

    Defines supported transport protocols for network service identification.

    Attributes:
        UDP (str): User Datagram Protocol for connectionless communication
        TCP (str): Transmission Control Protocol for reliable communication
    """

    UDP = "UDP"
    TCP = "TCP"


class PathType(models.TextChoices):
    """Web path and resource type classifications.

    Categorizes discovered web resources as API endpoints or file shares
    for targeted security analysis.

    Attributes:
        ENDPOINT (str): Web API endpoints and application paths
        SHARE (str): File shares and directory resources
    """

    ENDPOINT = "ENDPOINT"
    SHARE = "SHARE"


class TriageStatus(models.TextChoices):
    """Finding triage workflow status classifications.

    Represents the review state of security findings in the triage process
    for false positive elimination and confirmation.

    Attributes:
        FALSE_POSITIVE (str): Finding determined to be a false positive
        TRUE_POSITIVE (str): Finding confirmed as a legitimate security issue
        WONT_FIX (str): Legitimate finding but marked as won't fix
        UNTRIAGED (str): Finding has not been reviewed in triage process
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
TransportProtocol: type[Choices] = TransportProtocol
TriageStatus: type[Choices] = TriageStatus

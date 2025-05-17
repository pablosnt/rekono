from typing import Any

from django.db import models
from django.db.models.enums import Choices


class Severity(models.IntegerChoices):
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    def __str__(self) -> Any:
        return self.name.capitalize()


class OSINTDataType(models.TextChoices):
    IP = "IP"
    DOMAIN = "Domain"
    VHOST = "VHOST"
    URL = "URL"
    EMAIL = "Email"
    ASN = "ASN"
    USER = "Username"
    PASSWORD = "Password"


class HostOS(models.TextChoices):
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "MacOS"
    IOS = "iOS"
    ANDROID = "Android"
    SOLARIS = "Solaris"
    FREEBSD = "FreeBSD"
    OTHER = "Other"


class PortStatus(models.TextChoices):
    OPEN = "Open"
    OPEN_FILTERED = "Open - Filtered"
    FILTERED = "Filtered"
    CLOSED = "Closed"


class Protocol(models.TextChoices):
    UDP = "UDP"
    TCP = "TCP"


class PathType(models.TextChoices):
    ENDPOINT = "ENDPOINT"
    SHARE = "SHARE"


class TriageStatus(models.TextChoices):
    FALSE_POSITIVE = "False Positive"
    TRUE_POSITIVE = "True Positive"
    WONT_FIX = "Won't Fix"
    UNTRIAGED = "Untriaged"


# https://github.com/google/pytype/issues/1048
Severity: type[Choices] = Severity
OSINTDataType: type[Choices] = OSINTDataType
HostOS: type[Choices] = HostOS
PortStatus: type[Choices] = PortStatus
Protocol: type[Choices] = Protocol
TriageStatus: type[Choices] = TriageStatus

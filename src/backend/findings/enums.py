from enum import Enum  # https://github.com/google/pytype/issues/1048
from typing import Any

from django.db import models


class Severity(models.IntegerChoices, Enum):
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    def __str__(self) -> Any:
        return self.name.capitalize()


class OSINTDataType(models.TextChoices, Enum):
    IP = "IP"
    DOMAIN = "Domain"
    VHOST = "VHOST"
    URL = "URL"
    EMAIL = "Email"
    ASN = "ASN"
    USER = "Username"
    PASSWORD = "Password"


class HostOS(models.TextChoices, Enum):
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "MacOS"
    IOS = "iOS"
    ANDROID = "Android"
    SOLARIS = "Solaris"
    FREEBSD = "FreeBSD"
    OTHER = "Other"


class PortStatus(models.TextChoices, Enum):
    OPEN = "Open"
    OPEN_FILTERED = "Open - Filtered"
    FILTERED = "Filtered"
    CLOSED = "Closed"


class Protocol(models.TextChoices, Enum):
    UDP = "UDP"
    TCP = "TCP"


class PathType(models.TextChoices, Enum):
    ENDPOINT = "ENDPOINT"
    SHARE = "SHARE"


class TriageStatus(models.TextChoices, Enum):
    FALSE_POSITIVE = "False Positive"
    TRUE_POSITIVE = "True Positive"
    WONT_FIX = "Won't Fix"
    UNTRIAGED = "Untriaged"

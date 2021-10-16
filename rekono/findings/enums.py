from django.db import models


class Severity(models.IntegerChoices):
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class DataType(models.IntegerChoices):
    IP = 1
    DOMAIN = 2
    URL = 3
    MAIL = 4
    LINK = 5
    ASN = 6
    USER = 7
    PASSWORD = 8


class OSType(models.IntegerChoices):
    LINUX = 1
    WINDOWS = 2
    MACOS = 3
    IOS = 4
    ANDROID = 5
    SOLARIS = 6
    FREEBSD = 7
    OTHER = 8


class PortStatus(models.IntegerChoices):
    OPEN = 1
    OPEN_FILTERED = 2
    FILTERED = 3
    CLOSED = 4


class Protocol(models.IntegerChoices):
    UDP = 1
    TCP = 2

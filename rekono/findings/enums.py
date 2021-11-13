from django.db import models


class Severity(models.TextChoices):
    INFO = 'Info'
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    CRITICAL = 'Critical'


class DataType(models.TextChoices):
    IP = 'IP'
    DOMAIN = 'Domain'
    URL = 'Url'
    EMAIL = 'Email'
    LINK = 'Link'
    ASN = 'ASN'
    USER = 'Username'
    PASSWORD = 'Password'


class OSType(models.TextChoices):
    LINUX = 'Linux'
    WINDOWS = 'Windows'
    MACOS = 'MacOS'
    IOS = 'iOS'
    ANDROID = 'Android'
    SOLARIS = 'Solaris'
    FREEBSD = 'FreeBSD'
    OTHER = 'Other'


class PortStatus(models.TextChoices):
    OPEN = 'Open'
    OPEN_FILTERED = 'Open - Filtered'
    FILTERED = 'Filtered'
    CLOSED = 'Closed'


class Protocol(models.TextChoices):
    UDP = 'UDP'
    TCP = 'TCP'

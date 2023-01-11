from django.db import models


class Severity(models.TextChoices):
    '''Severity values to categorize findings, specially Vulnerability findings.'''

    INFO = 'Info'
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    CRITICAL = 'Critical'


class DataType(models.TextChoices):
    '''Data types to categorize OSINT findings.'''

    IP = 'IP'
    DOMAIN = 'Domain'
    VHOST = 'VHOST'
    URL = 'Url'
    EMAIL = 'Email'
    LINK = 'Link'
    ASN = 'ASN'
    USER = 'Username'
    PASSWORD = 'Password'


class OSType(models.TextChoices):
    '''OS types to categorize Host findings.'''

    LINUX = 'Linux'
    WINDOWS = 'Windows'
    MACOS = 'MacOS'
    IOS = 'iOS'
    ANDROID = 'Android'
    SOLARIS = 'Solaris'
    FREEBSD = 'FreeBSD'
    OTHER = 'Other'


class PortStatus(models.TextChoices):
    '''Port statuses to categorize ports.'''

    OPEN = 'Open'
    OPEN_FILTERED = 'Open - Filtered'
    FILTERED = 'Filtered'
    CLOSED = 'Closed'


class Protocol(models.TextChoices):
    '''Protocols to categorize Port services.'''

    UDP = 'UDP'
    TCP = 'TCP'


class PathType(models.TextChoices):
    '''Protocols to categorize Paths.'''

    ENDPOINT = 'ENDPOINT'
    SHARE = 'SHARE'

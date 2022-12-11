from enum import Enum

from django.db import models


class InputTypeNames(models.TextChoices):
    '''Input type names, related to findings and resources.'''

    OSINT = 'OSINT'
    HOST = 'Host'
    PORT = 'Port'
    PATH = 'Path'
    TECHNOLOGY = 'Technology'
    VULNERABILITY = 'Vulnerability'
    EXPLOIT = 'Exploit'
    CREDENTIAL = 'Credential'
    WORDLIST = 'Wordlist'


class InputKeyword(Enum):
    '''List of keywords that can be included in tool argument patterns to include BaseInput data.'''

    TARGET = 1
    HOST = 2
    PORT = 3
    PORTS = 4
    PORTS_COMMAS = 5
    TECHNOLOGY = 6
    VERSION = 7
    ENDPOINT = 8
    URL = 9
    EMAIL = 10
    USERNAME = 11
    SECRET = 12
    CVE = 13
    EXPLOIT = 14
    WORDLIST = 15
    COOKIE_NAME = 16
    TOKEN = 17
    CREDENTIAL_TYPE = 18
    CREDENTIAL_TYPE_LOWER = 19

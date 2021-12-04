from django.db import models

# Create your enums here.


class IntensityRank(models.IntegerChoices):
    SNEAKY = 1
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5


class FindingType(models.TextChoices):
    OSINT = 'OSINT'
    HOST = 'Host'
    ENUMERATION = 'Enumeration'
    ENDPOINT = 'Endpoint'
    TECHNOLOGY = 'Technology'
    VULNERABILITY = 'Vulnerability'
    EXPLOIT = 'Exploit'
    CREDENTIAL = 'Credential'
    WORDLIST = 'Wordlist'


class Stage(models.IntegerChoices):
    OSINT = 1
    ENUMERATION = 2
    VULNERABILITIES = 3
    SERVICES = 4
    EXPLOITATION = 5


class InputSelection(models.TextChoices):
    ALL = 'All'
    FOR_EACH = 'For Each'

from django.db import models

# Create your enums here.


class IntensityRank(models.TextChoices):
    SNEAKY = 'Sneaky'
    LOW = 'Low'
    NORMAL = 'Normal'
    HARD = 'Hard'
    INSANE = 'Insane'


class FindingType(models.TextChoices):
    OSINT = 'OSINT'
    HOST = 'Host'
    ENUMERATION = 'Enumeration'
    ENDPOINT = 'Endpoint'
    TECHNOLOGY = 'Technology'
    VULNERABILITY = 'Vulnerability'
    EXPLOIT = 'Exploit'
    PARAMETER = 'Parameter'
    CREDENTIAL = 'Credential'


class Stage(models.TextChoices):
    OSINT = 'OSINT'
    ENUMERATION = 'Enumeration'
    VULNERABILITIES = 'Vulnerabilities analysis'
    SERVICES = 'Services analysis'
    EXPLOITATION = 'Exploitation'


class InputSelection(models.TextChoices):
    ALL = 'All'
    FOR_EACH = 'For Each'

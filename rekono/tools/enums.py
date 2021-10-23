from django.db import models

# Create your enums here.


class IntensityRank(models.IntegerChoices):
    SNEAKY = 1
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5


class FindingType(models.IntegerChoices):
    OSINT = 1
    HOST = 2
    ENUMERATION = 3
    HTTP_ENDPOINT = 4
    TECHNOLOGY = 5
    VULNERABILITY = 6
    EXPLOIT = 7
    PARAMETER = 8
    CREDENTIAL = 9


class Stage(models.IntegerChoices):
    OSINT = 1
    ENUMERATION = 2
    VULNERABILITIES = 3
    SERVICES = 4
    EXPLOITATION = 5


class InputSelection(models.IntegerChoices):
    ALL = 1
    FOR_EACH = 2

from django.db import models

# Create your enums here.


class IntensityRank(models.IntegerChoices):
    SNEAKY = 1
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5


class Stage(models.IntegerChoices):
    OSINT = 1
    ENUMERATION = 2
    VULNERABILITIES = 3
    SERVICES = 4
    EXPLOITATION = 5

from django.db import models

# Create your enums here.


class IntensityRank(models.IntegerChoices):
    '''Intensity ranks.'''

    SNEAKY = 1                                                                  # Softest
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5                                                                  # Hardest


class Stage(models.IntegerChoices):
    '''Stage names.'''

    OSINT = 1
    ENUMERATION = 2
    VULNERABILITIES = 3
    SERVICES = 4
    EXPLOITATION = 5

# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db import models

# Create your enums here.


class Intensity(models.IntegerChoices):
    SNEAKY = 1  # Softest
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5  # Hardest


class Stage(models.IntegerChoices):
    OSINT = 1
    ENUMERATION = 2
    VULNERABILITIES = 3
    SERVICES = 4
    EXPLOITATION = 5

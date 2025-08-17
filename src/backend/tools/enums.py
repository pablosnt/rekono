from django.db import models
from django.db.models.enums import Choices


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


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Intensity: type[Choices] = Intensity
Stage: type[Stage] = Stage

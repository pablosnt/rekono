from django.db import models
from django.db.models.enums import Choices


class TimeUnit(models.TextChoices):
    MINUTES = "Minutes"
    HOURS = "Hours"
    DAYS = "Days"
    WEEKS = "Weeks"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
TimeUnit: type[Choices] = TimeUnit

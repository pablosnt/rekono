from django.db import models
from django.db.models.enums import Choices


class TimeUnit(models.TextChoices):
    """Time units supported for Task scheduling and repeating configuration."""

    MINUTES = "Minutes"
    HOURS = "Hours"
    DAYS = "Days"
    WEEKS = "Weeks"


TimeUnit: type[Choices] = TimeUnit  # https://github.com/google/pytype/issues/1048

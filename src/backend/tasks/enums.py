# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db import models


class TimeUnit(models.TextChoices):
    """Time units supported for Task scheduling and repeating configuration."""

    MINUTES = "Minutes"
    HOURS = "Hours"
    DAYS = "Days"
    WEEKS = "Weeks"

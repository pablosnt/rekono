"""Enumeration classes for task scheduling and timing.

Defines enumeration values used throughout the task management system
for specifying time units in recurring task scheduling.
"""

from django.db import models
from django.db.models.enums import Choices


class TimeUnit(models.TextChoices):
    """Enumeration of supported time units for recurring task scheduling.

    Defines the available time units that can be used with repeat intervals
    for scheduled and recurring tasks.

    Attributes:
        MINUTES (str): Minutes time unit for short-interval recurring tasks
        HOURS (str): Hours time unit for hourly recurring tasks
        DAYS (str): Days time unit for daily recurring tasks
        WEEKS (str): Weeks time unit for weekly recurring tasks
    """

    MINUTES = "Minutes"
    HOURS = "Hours"
    DAYS = "Days"
    WEEKS = "Weeks"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
TimeUnit: type[Choices] = TimeUnit

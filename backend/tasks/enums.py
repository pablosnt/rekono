"""Time units used to schedule the repetition of the tasks."""

from django.db import models
from django.db.models.enums import Choices


class TimeUnit(models.TextChoices):
    """Unit of the interval between two executions of a repeated task."""

    MINUTES = "Minutes"
    HOURS = "Hours"
    DAYS = "Days"
    WEEKS = "Weeks"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
TimeUnit: type[Choices] = TimeUnit

from django.db import models


class TimeUnit(models.TextChoices):
    """Time units supported for Task scheduling and repeating configuration."""

    MINUTES = "Minutes"
    HOURS = "Hours"
    DAYS = "Days"
    WEEKS = "Weeks"

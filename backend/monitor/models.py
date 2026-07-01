"""Django models for automated threat intelligence monitoring.

Provides the MonitorSettings model for configuring background monitoring
jobs that periodically query external threat intelligence sources such as
CveCrowd and First/EPSS. Settings follow a singleton pattern controlling
the interval between monitoring runs.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseModel


class MonitorSettings(BaseModel):
    """Model for configuring automated threat intelligence monitoring.

    Manages configuration for background monitoring jobs that periodically query
    external threat intelligence sources.
    Follows a singleton pattern - only one instance should exist.

    The monitoring system schedules itself using RQ jobs and triggers monitoring
    alerts when needed.

    Attributes:
        rq_job_id (TextField): ID of the current scheduled monitoring job
        last_monitor (DateTimeField): Timestamp of the last monitoring execution
        hour_span (IntegerField): Hours between monitoring runs (24-168 hours)

    Example:
        Configure monitoring to run every 48 hours:

        ```python
        settings = MonitorSettings.objects.first()
        settings.hour_span = 48
        settings.save()
        ```
    """

    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    last_monitor = models.DateTimeField(blank=True, null=True)
    hour_span = models.IntegerField(default=24, validators=[MinValueValidator(24), MaxValueValidator(168)])

    def __str__(self) -> str:
        """Return string representation of monitor settings.

        Returns:
            str: Description of last monitor time and next scheduled run
        """
        return f"Last monitor was at {self.last_monitor}. Next one in {self.hour_span} hours"

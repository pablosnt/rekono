"""Model of the monitor configuration."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseModel


class MonitorSettings(BaseModel):
    """Configuration of the monitor job, of which only one instance exists.

    Attributes:
        rq_job_id: Identifier of the scheduled job, used to know if the monitor is
          already running before enqueuing a new one.
        last_monitor: Date when the monitor ran for the last time.
        hour_span: Hours between two monitor runs, from one day to one week.
    """

    rq_job_id = models.TextField(max_length=50, blank=True, null=True)
    last_monitor = models.DateTimeField(blank=True, null=True)
    hour_span = models.IntegerField(default=24, validators=[MinValueValidator(24), MaxValueValidator(168)])

    def __str__(self) -> str:
        """Return when the monitor ran and when it will run again."""
        return f"Last monitor was at {self.last_monitor}. Next one in {self.hour_span} hours"

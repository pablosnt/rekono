"""Models of the CVE Crowd configuration and of the trending CVEs.

Typical usage example:

  settings = CveCrowdSettings.objects.first()
  settings.secret = "..."  # encrypted into _api_token on save
  settings.save()
"""

from django.db import models

from framework.models import BaseEncrypted, BaseModel
from security.validators.input_validator import Regex, Validator


class CveCrowdSettings(BaseEncrypted):
    """Configuration of CVE Crowd, of which only one instance exists.

    Attributes:
        trending_span_days: Days that a CVE has to have been discussed in to be
          considered trending.
        execute_per_execution: Whether the vulnerabilities are checked as soon as
          they are discovered, instead of only by the monitor job.
        is_available: Whether the platform answered the last time that the API
          token was saved, which is when it's checked.
    """

    _api_token = models.TextField(
        max_length=100,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )
    trending_span_days = models.IntegerField(choices=[(1, "1 day"), (7, "7 days"), (30, "30 days")], default=1)
    execute_per_execution = models.BooleanField(default=True)
    is_available = models.BooleanField(default=False)

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return the name of the platform."""
        return "CVE Crowd"


class CveCrowdCache(BaseModel):
    """CVE that was trending when CVE Crowd was asked for the last time.

    The whole list is replaced once a day, so the executions don't ask for it
    again and again while they process their findings.

    Attributes:
        cve: CVE identifier that was trending.
        date: Date when CVE Crowd reported it.
    """

    cve = models.TextField(max_length=20)
    date = models.DateTimeField()

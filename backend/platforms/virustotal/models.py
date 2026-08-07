"""Model of the VirusTotal configuration.

Typical usage example:

  settings = VirusTotalSettings.objects.first()
  settings.secret = "..."  # encrypted into _api_token on save
  settings.save()
"""

from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class VirusTotalSettings(BaseEncrypted):
    """Configuration of VirusTotal, of which only one instance exists.

    Attributes:
        is_available: Whether the platform answered the last time that the API
          token was saved, which is when it's checked, since asking VirusTotal on
          every finding would waste the requests that the token allows.
    """

    _api_token = models.TextField(
        max_length=64,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )
    is_available = models.BooleanField(default=False)

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return the name of the platform."""
        return "Virus Total"

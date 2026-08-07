"""Model of the VulnCheck configuration.

Typical usage example:

  settings = VulnCheckSettings.objects.first()
  settings.secret = "..."  # encrypted into _api_token on save
  settings.save()
"""

from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class VulnCheckSettings(BaseEncrypted):
    """Configuration of VulnCheck, of which only one instance exists.

    Without the API token the platform can't be used, since VulnCheck rejects the
    requests that aren't authenticated.
    """

    _api_token = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return the name of the platform."""
        return "VulnCheck"

"""Model of the NVD NIST configuration.

Typical usage example:

  settings = NvdNistSettings.objects.first()
  settings.secret = "..."  # encrypted into _api_token on save
  settings.save()
"""

from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class NvdNistSettings(BaseEncrypted):
    """Configuration of NVD NIST, of which only one instance exists.

    The API token is optional, since NVD answers without it, only slower.
    """

    _api_token = models.TextField(
        max_length=50,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return the name of the platform."""
        return "NVD NIST"

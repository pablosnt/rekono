"""Model of the SMTP configuration.

Typical usage example:

  settings = SMTPSettings.objects.first()
  settings.secret = "..."  # encrypted into _password on save
  settings.save()
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class SMTPSettings(BaseEncrypted):
    """Configuration of the SMTP server, of which only one instance exists.

    Attributes:
        host: Address of the SMTP server that sends the emails.
        port: Port where that server listens.
        username: User that Rekono authenticates as.
        tls: Whether the connection with the server must be encrypted.
    """

    host = models.TextField(max_length=100, validators=[Validator(Regex.TARGET)], blank=True, null=True)
    port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)], blank=True, null=True, default=587
    )
    username = models.TextField(max_length=100, validators=[Validator(Regex.NAME, code="name")], null=True, blank=True)
    _password = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="password",
    )
    tls = models.BooleanField(default=True)

    _encrypted_field = "_password"

    def __str__(self) -> str:
        """Return the server that sends the emails, as the literal "None" if there is none."""
        return f"{self.host}:{self.port}" if self.host and self.port else "None"

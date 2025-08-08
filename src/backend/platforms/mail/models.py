"""Django models for SMTP email configuration management.

Provides the SMTPSettings model for storing and managing SMTP server configuration
with automatic encryption of sensitive credential data. Supports TLS connections
and comprehensive validation for secure email delivery.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class SMTPSettings(BaseEncrypted):
    """Model representing SMTP server configuration for email notifications.

    Stores SMTP server connection parameters with automatic encryption of sensitive
    credentials. Supports TLS/SSL connections for secure email delivery and includes
    comprehensive validation for all configuration parameters.

    Attributes:
        host (TextField): SMTP server hostname or IP address (max 100 chars)
        port (IntegerField): SMTP server port number (0-65535, default 587)
        username (TextField): SMTP authentication username (max 100 chars)
        _password (TextField): Encrypted SMTP authentication password (max 200 chars)
        tls (BooleanField): Enable TLS encryption for SMTP connections (default True)

    Example:
        Configure SMTP settings for Gmail:

        ```python
        smtp_config = SMTPSettings.objects.create(
            host="smtp.gmail.com",
            port=587,
            username="notifications@company.com",
            secret="app_password_here",
            tls=True
        )
        ```
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
        """Return string representation of SMTP settings.

        Returns:
            str: SMTP server in format "host:port" or "None" if not configured
        """
        return f"{self.host}:{self.port}" if self.host and self.port else "None"

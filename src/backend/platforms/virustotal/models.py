"""Django models for VirusTotal platform configuration and settings.

This module defines the data models for VirusTotal integration configuration,
providing secure storage for API credentials and platform settings. The models
support encrypted field storage to protect sensitive API tokens and maintain
compliance with security best practices.
"""

from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class VirusTotalSettings(BaseEncrypted):
    """Model for storing VirusTotal platform configuration and API credentials.

    Manages secure storage of VirusTotal API authentication tokens and platform
    configuration settings. Uses field-level encryption to protect sensitive
    API credentials and follows singleton pattern for global platform settings.

    Attributes:
        _api_token (TextField): Encrypted VirusTotal API token for authentication.
                               Validated using SECRET regex pattern for security.

    Example:
        Configure VirusTotal API credentials:

        ```python
        settings = VirusTotalSettings.objects.first()
        settings.secret = "your_virustotal_api_token_here"
        settings.save()
        ```

    Note:
        This model follows a singleton pattern - only one instance should exist
        to maintain global platform configuration consistency.
    """

    _api_token = models.TextField(
        max_length=64,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return string representation of VirusTotal settings.

        Returns:
            str: Human-readable name of the VirusTotal platform.
        """
        return "Virus Total"

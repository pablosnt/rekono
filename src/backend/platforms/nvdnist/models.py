"""Django models for NVD NIST platform configuration and settings.

Provides the NvdNistSettings model for managing API authentication credentials
and configuration parameters for National Vulnerability Database integration.
Supports secure token storage with encryption and validation.
"""

from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class NvdNistSettings(BaseEncrypted):
    """Model for NVD NIST API configuration and authentication settings.

    Manages API token credentials and configuration for NVD NIST vulnerability
    intelligence integration. Supports encrypted storage of sensitive API tokens
    with automatic encryption/decryption through the BaseEncrypted framework.

    Attributes:
        _api_token (TextField): Encrypted NVD API token for enhanced access (max 50 chars)
        _encrypted_field (str): Field name for encryption configuration

    Example:
        Configure NVD NIST API integration:

        ```python
        settings = NvdNistSettings.objects.first()
        settings.secret = "your-nvd-api-token"
        settings.save()
        ```
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
        """Return string representation of NVD NIST settings.

        Returns:
            str: Platform name identifier for display purposes.
        """
        return "NVD NIST"

"""Django models for VulnCheck platform configuration and settings.

Provides the VulnCheckSettings model for managing the Bearer API token required
to authenticate requests to the VulnCheck NVD++ vulnerability intelligence service.
Supports secure token storage with encryption and validation.
"""

from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class VulnCheckSettings(BaseEncrypted):
    """Model for VulnCheck API configuration and authentication settings.

    Manages the Bearer API token required for authenticating requests to the
    VulnCheck NVD++ service. Supports encrypted storage of sensitive tokens
    with automatic encryption/decryption through the BaseEncrypted framework.
    The token field allows up to 200 characters to accommodate JWT-style tokens.

    Attributes:
        _api_token (TextField): Encrypted VulnCheck Bearer token (max 200 chars)
        _encrypted_field (str): Field name for encryption configuration

    Example:
        Configure VulnCheck API integration:

        ```python
        settings = VulnCheckSettings.objects.first()
        settings.secret = "your-vulncheck-api-token"
        settings.save()
        ```
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
        """Return string representation of VulnCheck settings.

        Returns:
            str: Platform name identifier for display purposes.
        """
        return "VulnCheck"

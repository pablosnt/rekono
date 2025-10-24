"""Django models for CVE Crowd platform integration settings.

This module provides the core data model for CVE Crowd platform configuration,
enabling secure storage of API credentials and monitoring settings. The model
supports encrypted credential storage and configurable trending analysis parameters
for comprehensive vulnerability threat intelligence integration.

Architecture:
    The settings model extends BaseEncrypted to provide automatic encryption for
    sensitive API credentials while maintaining flexible configuration options
    for trending analysis timeframes and execution patterns within the security
    assessment workflow.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class CveCrowdSettings(BaseEncrypted):
    """Model for CVE Crowd platform integration configuration.

    Represents configuration settings for the CVE Crowd threat intelligence
    platform integration, providing encrypted API credential storage and
    customizable trending analysis parameters for automated vulnerability
    monitoring and prioritization.

    Attributes:
        _api_token (TextField): Encrypted CVE Crowd API bearer token (max 50 chars)
        trending_span_days (IntegerField): Days for trending analysis (1-7, default 7)
        execute_per_execution (BooleanField): Enable per-execution processing (default True)

    Example:
        Configure CVE Crowd integration with 3-day trending window:

        ```python
        settings = CveCrowdSettings.objects.create(
            trending_span_days=3,
            execute_per_execution=True
        )
        settings.secret = "your_api_token_here"
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
    trending_span_days = models.IntegerField(default=7, validators=[MinValueValidator(1), MaxValueValidator(7)])
    execute_per_execution = models.BooleanField(default=True)

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return string representation of the CVE Crowd settings.

        Returns:
            str: Platform name "CVE Crowd".
        """
        return "CVE Crowd"

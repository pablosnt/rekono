"""Django models for CVE Crowd platform integration settings.

This module provides the data models for CVE Crowd platform configuration,
enabling secure storage of API credentials, monitoring settings, and a
database-backed cache for trending CVE data. The settings model supports
encrypted credential storage and configurable trending analysis parameters
for comprehensive vulnerability threat intelligence integration.

Architecture:
    The settings model extends BaseEncrypted to provide automatic encryption for
    sensitive API credentials while maintaining flexible configuration options
    for trending analysis timeframes and execution patterns within the security
    assessment workflow. The cache model stores trending CVE identifiers to
    avoid redundant API requests across multiple executions.
"""

from django.db import models

from framework.models import BaseEncrypted, BaseModel
from security.validators.input_validator import Regex, Validator


class CveCrowdSettings(BaseEncrypted):
    """Model for CVE Crowd platform integration configuration.

    Represents configuration settings for the CVE Crowd threat intelligence
    platform integration, providing encrypted API credential storage and
    customizable trending analysis parameters for automated vulnerability
    monitoring and prioritization.

    Attributes:
        _api_token (TextField): Encrypted CVE Crowd API bearer token (max 50 chars).
        trending_span_days (IntegerField): Days for trending analysis (1, 7, or 30, default 1).
        execute_per_execution (BooleanField): Enable per-execution processing (default True).
        is_available (BooleanField): Cached platform availability status (default False).

    Example:
        Configure CVE Crowd integration with a 7-day trending window:

        ```python
        settings = CveCrowdSettings.objects.first()
        settings.trending_span_days = 7
        settings.secret = "your_api_token_here"
        settings.save()
        ```
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
        """Return string representation of the CVE Crowd settings.

        Returns:
            str: Platform name "CVE Crowd".
        """
        return "CVE Crowd"


class CveCrowdCache(BaseModel):
    """Cache model for trending CVE identifiers retrieved from the CVE Crowd API.

    Stores CVE identifiers with their retrieval timestamp to avoid redundant API
    requests. The cache is considered valid for one day; existing entries are
    deleted and replaced with a fresh set whenever the cache is expired or a
    forced refresh is triggered.

    Attributes:
        cve (TextField): CVE identifier (e.g., CVE-2024-12345), max 20 chars.
        date (DateTimeField): Timestamp when this entry was stored in the cache.
    """

    cve = models.TextField(max_length=20)
    date = models.DateTimeField()

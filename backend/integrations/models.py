"""Django models for third-party integration management.

This module provides the core data models for Rekono's external platform integration
system, which enables administrators to configure and manage connections to external
security tools, vulnerability databases, and reporting platforms. The integration
system provides centralized configuration management with administrative controls.

Architecture:
    The integration system uses a simple model-based approach where each integration
    is represented by a single record containing configuration metadata, status
    controls, and documentation references. This design allows for easy extension
    and management of new integration types.
"""

from django.db import models

from framework.models import BaseModel


class Integration(BaseModel):
    """Model representing external platform integrations for security tools.

    Represents third-party platform integrations that extend Rekono's capabilities
    through external APIs, vulnerability databases, and security tool connections.
    Each integration includes configuration metadata, administrative controls, and
    documentation references for proper setup and usage.

    Attributes:
        key (TextField): Identifier key matched against a platform class's lowercased
                        name for integration lookups, e.g. by BaseIntegration.integration
                        (max 100 chars)
        name (TextField): Display name for the integration (max 100 chars)
        description (TextField): Detailed description of integration functionality (max 500 chars)
        enabled (BooleanField): Whether this integration is currently active (default: True)
        reference (TextField): Documentation or configuration reference URL (max 250 chars)
        icon (TextField): Optional icon URL for UI display (max 250 chars)

    Example:
        Create a new vulnerability database integration:

        ```python
        integration = Integration.objects.create(
            key="nvdnist",
            name="NVD NIST",
            description="Integration with NIST NVD for CVE data enrichment",
            reference="https://nvd.nist.gov/developers",
            icon="https://example.com/nvd-icon.png"
        )
        ```
    """

    key = models.TextField(max_length=100, unique=True)
    name = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    enabled = models.BooleanField(default=True)
    reference = models.TextField(max_length=250)
    icon = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        """Return string representation of the integration.

        Returns:
            str: The display name of the integration.
        """
        return self.name

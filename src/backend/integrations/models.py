"""Integration models for managing external service integrations in Rekono.

This module provides the Integration model which defines external services and
platforms that can be integrated with Rekono. Each integration represents a
connection to an external system that can be enabled or disabled as needed.
"""

from django.db import models

from framework.models import BaseModel


class Integration(BaseModel):
    """Model for managing external service integrations.

    This model represents external services, platforms, or tools that can be
    integrated with Rekono. Each integration can be enabled or disabled to
    control its availability and functionality within the system.

    Integrations typically represent connections to external APIs, services,
    or platforms that provide additional functionality to Rekono users.

    Attributes:
        key: Unique identifier for the integration (max 100 characters).
        name: Human-readable name for the integration (max 100 characters).
        description: Detailed description of the integration's purpose and
            functionality (max 500 characters).
        enabled: Boolean flag indicating whether the integration is active.
        reference: Reference identifier or URL for the integration (max 250
            characters).
        icon: URL or path to the integration's icon/image (max 250 characters,
            optional).
    """

    key = models.TextField(max_length=100)
    name = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    enabled = models.BooleanField(default=True)
    reference = models.TextField(max_length=250)
    icon = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        """Return string representation of the integration.

        Returns:
            The name of the integration.
        """
        return self.name

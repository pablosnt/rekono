"""Model of the external platforms that Rekono can work with."""

from django.db import models

from framework.models import BaseModel


class Integration(BaseModel):
    """External platform that Rekono can work with.

    Attributes:
        key: Name of the platform class in lowercase, which is how a platform
          finds its own integration.
        name: Name of the platform, as it's shown to the users.
        description: What Rekono uses the platform for.
        enabled: Whether Rekono must use the platform.
        reference: Link to the documentation of the platform.
        icon: Link to the logo of the platform.
    """

    key = models.TextField(max_length=100, unique=True)
    name = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    enabled = models.BooleanField(default=True)
    reference = models.TextField(max_length=250)
    icon = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        """Return the name of the platform."""
        return self.name

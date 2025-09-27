"""Django application configuration for integrations module.

Configures the integrations application with custom fixture loading logic
to preserve user-disabled integration states across deployments.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    """Configuration class for the integrations Django application.

    Extends BaseApp to provide custom fixture loading behavior that preserves
    user-configured integration enabled/disabled states across deployments.

    Attributes:
        name (str): The Django application name
    """

    name = "integrations"

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load integration fixtures while preserving user disabled states.

        Captures currently disabled integrations before fixture loading and
        re-disables them after loading to preserve user configuration choices.

        Args:
            **kwargs: Additional arguments passed to parent fixture loading method

        Note:
            This ensures that user-disabled integrations remain disabled even
            after fixture reloading during deployments or updates.
        """
        from integrations.models import Integration

        # Capture currently disabled integrations before loading fixtures
        disabled_integrations = Integration.objects.filter(enabled=False).values_list("id", flat=True)
        # Load fixtures using parent class method
        super().load_fixtures(**kwargs)
        # Re-disable integrations that were previously disabled by users
        Integration.objects.filter(id__in=disabled_integrations).update(enabled=False)

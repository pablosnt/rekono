"""Django app configuration for the integrations app.

This module defines the Django app configuration for the integrations
application, extending the base app configuration with integration-specific
functionality including custom fixture loading logic.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    """Django app configuration for the integrations application.

    This configuration class extends both Django's AppConfig and the project's
    BaseApp to provide integration-specific functionality and custom fixture
    loading behavior.

    The app includes custom fixture loading logic that preserves the enabled
    status of integrations that were previously disabled, ensuring that user
    preferences are maintained across fixture updates.
    """

    name = "integrations"

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load fixtures while preserving disabled integration states.

        This method overrides the default fixture loading behavior to ensure
        that integrations that were previously disabled by users remain disabled
        after fixture updates. This prevents automatic re-enabling of integrations
        that users have specifically disabled.

        Args:
            **kwargs: Additional keyword arguments passed to the parent method.
        """
        from integrations.models import Integration

        # Capture currently disabled integrations before loading fixtures
        disabled_integrations = Integration.objects.filter(enabled=False).values_list("id", flat=True)
        # Load fixtures using parent class method
        super().load_fixtures(**kwargs)
        # Re-disable integrations that were previously disabled by users
        Integration.objects.filter(id__in=disabled_integrations).update(enabled=False)

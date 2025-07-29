"""Django app configuration for alerts module.

This module contains the Django app configuration for the alerts application,
including model registration and fixture handling.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class AlertsConfig(BaseApp, AppConfig):
    """Django app configuration for alerts.

    Configures the alerts Django application, including model registration
    and fixture loading behavior.

    Attributes:
        name: The name of the Django app
        skip_fixtures_if_model_exists: Whether to skip fixtures if models exist
    """

    name = "alerts"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the models that should be registered with this app.

        Returns:
            List of model classes to register
        """
        from alerts.models import MonitorSettings

        return [MonitorSettings]

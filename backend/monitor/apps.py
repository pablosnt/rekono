"""Django app configuration for monitor module.

Contains the Django app configuration for the monitor application,
including model registration and fixture handling.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class MonitorConfig(BaseApp, AppConfig):
    """Django app configuration for monitor.

    Configures the monitor Django application with model registration
    and fixture loading behavior.

    Attributes:
        name (str): The name of the Django app
        skip_fixtures_if_model_exists (bool): Skip fixtures if models exist
    """

    name = "monitor"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the models that should be registered with this app.

        Returns:
            list[Any]: Model classes to register for fixture loading
        """
        from monitor.models import MonitorSettings

        return [MonitorSettings]

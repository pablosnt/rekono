"""Django app configuration of the monitor app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class MonitorConfig(BaseApp, AppConfig):
    """Configuration of the monitor app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "monitor"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the monitor settings model, whose data comes from the fixtures.

        Returns:
            The monitor settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from monitor.models import MonitorSettings

        return [MonitorSettings]

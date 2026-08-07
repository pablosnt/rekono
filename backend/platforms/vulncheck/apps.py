"""Django app configuration of the VulnCheck app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class VulncheckConfig(BaseApp, AppConfig):
    """Configuration of the VulnCheck app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.vulncheck"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the VulnCheck settings model, whose data comes from the fixtures.

        Returns:
            The VulnCheck settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.vulncheck.models import VulnCheckSettings

        return [VulnCheckSettings]

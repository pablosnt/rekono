"""Django app configuration of the DefectDojo app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class DefectDojoConfig(BaseApp, AppConfig):
    """Configuration of the DefectDojo app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.defectdojo"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the DefectDojo settings model, whose data comes from the fixtures.

        Returns:
            The DefectDojo settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.defectdojo.models import DefectDojoSettings

        return [DefectDojoSettings]

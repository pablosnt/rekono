"""Django app configuration of the VirusTotal app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class VirustotalConfig(BaseApp, AppConfig):
    """Configuration of the VirusTotal app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.virustotal"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the VirusTotal settings model, whose data comes from the fixtures.

        Returns:
            The VirusTotal settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.virustotal.models import VirusTotalSettings

        return [VirusTotalSettings]

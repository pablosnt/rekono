"""Django app configuration of the CVE Crowd app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class CvecrowdConfig(BaseApp, AppConfig):
    """Configuration of the CVE Crowd app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.cvecrowd"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the CVE Crowd settings model, whose data comes from the fixtures.

        Returns:
            The CVE Crowd settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.cvecrowd.models import CveCrowdSettings

        return [CveCrowdSettings]

"""Django app configuration of the NVD NIST app."""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class NvdnistConfig(BaseApp, AppConfig):
    """Configuration of the NVD NIST app.

    Attributes:
        name: Name of the app in the Django app registry.
        skip_fixtures_if_model_exists: The settings are only created once, so the
          configuration of a deployment is never overwritten.
    """

    name = "platforms.nvdnist"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the NVD NIST settings model, whose data comes from the fixtures.

        Returns:
            The NVD NIST settings model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from platforms.nvdnist.models import NvdNistSettings

        return [NvdNistSettings]

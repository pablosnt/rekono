"""Django application configuration for NVD NIST platform integration.

Configures the NVD NIST platform application with proper model registration
and initialization settings for vulnerability intelligence integration.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class NvdnistConfig(BaseApp, AppConfig):
    """Configuration class for NVD NIST platform application.

    Extends BaseApp and AppConfig to provide proper Django application
    setup with model registration and fixture management.

    Attributes:
        name (str): Application name for Django registration
        skip_fixtures_if_model_exists (bool): Fixture loading optimization flag
    """
    name = "platforms.nvdnist"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for this application.

        Returns the NvdNistSettings model for fixture loading and
        application initialization processes.

        Returns:
            list[Any]: List containing NvdNistSettings model class
        """
        from platforms.nvdnist.models import NvdNistSettings

        return [NvdNistSettings]

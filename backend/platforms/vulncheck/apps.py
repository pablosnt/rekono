"""Django application configuration for VulnCheck platform integration.

Configures the VulnCheck platform application with proper model registration
and initialization settings for NVD++ vulnerability intelligence integration.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class VulncheckConfig(BaseApp, AppConfig):
    """Configuration class for VulnCheck platform application.

    Extends BaseApp and AppConfig to provide proper Django application
    setup with model registration and fixture management.

    Attributes:
        name (str): Application name for Django registration
        skip_fixtures_if_model_exists (bool): Fixture loading optimization flag
    """

    name = "platforms.vulncheck"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for this application.

        Returns the VulnCheckSettings model for fixture loading and
        application initialization processes.

        Returns:
            list[Any]: List containing VulnCheckSettings model class.
        """
        from platforms.vulncheck.models import VulnCheckSettings

        return [VulnCheckSettings]

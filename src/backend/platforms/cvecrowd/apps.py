"""Django application configuration for CVE Crowd platform integration.

Provides application configuration for the CVE Crowd module with fixture
management and model registration for threat intelligence integration.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class CvecrowdConfig(BaseApp, AppConfig):
    """Django application configuration for the CVE Crowd platform module.

    Configures the CVE Crowd application with fixture management and
    model registration for threat intelligence platform integration.

    Attributes:
        name (str): Application name for Django registration
        skip_fixtures_if_model_exists (bool): Skip fixture loading if models exist
    """

    name = "platforms.cvecrowd"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the model classes for this application.

        Returns:
            list[Any]: List containing CveCrowdSettings model class.
        """
        from platforms.cvecrowd.models import CveCrowdSettings

        return [CveCrowdSettings]

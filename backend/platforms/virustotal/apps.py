"""Django application configuration for VirusTotal platform integration.

This module defines the Django application configuration for the VirusTotal
platform integration, including model loading and initialization settings.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class VirustotalConfig(BaseApp, AppConfig):
    """Django application configuration for VirusTotal platform integration.

    Configures the VirusTotal platform application with proper model loading
    and initialization settings. Inherits from BaseApp for common platform
    functionality and AppConfig for Django application management.

    Attributes:
        name (str): Fully qualified application name
        skip_fixtures_if_model_exists (bool): Skip loading fixtures if models exist
    """

    name = "platforms.virustotal"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for this application.

        Returns the list of Django models that belong to this application
        for initialization and fixture loading purposes.

        Returns:
            list[Any]: List of model classes for the VirusTotal application
        """
        from platforms.virustotal.models import VirusTotalSettings

        return [VirusTotalSettings]

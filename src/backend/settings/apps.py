"""Settings Django application configuration.

This module provides Django application configuration for the Settings module,
handling initialization, model registration, and fixture management for the
global configuration system.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class SettingsConfig(BaseApp, AppConfig):
    """Django application configuration for Settings module.

    Configures the Settings application within the Django framework, managing
    model initialization and fixture loading for global platform configuration.
    Inherits from BaseApp to integrate with Rekono's application framework.

    Attributes:
        name (str): Application name identifier for Django registration.
        skip_fixtures_if_model_exists (bool): Prevents fixture loading conflicts.
    """

    name = "settings"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Retrieve Settings model classes for framework integration.

        Returns the list of model classes managed by this application for
        registration with the Rekono framework and fixture management.

        Returns:
            list[Any]: List containing Settings model class for framework registration.
        """
        from settings.models import Settings

        return [Settings]

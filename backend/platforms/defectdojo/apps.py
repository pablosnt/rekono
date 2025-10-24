"""Django application configuration for DefectDojo integration platform.

Configures the DefectDojo integration application with base functionality and
model initialization for OWASP DefectDojo vulnerability management integration.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class DefectDojoConfig(BaseApp, AppConfig):
    """Django application configuration for DefectDojo integration platform.

    Configures the DefectDojo integration with DefectDojoSettings model initialization
    and fixture management. Extends BaseApp for consistent application configuration
    across the Rekono platform.

    Attributes:
        name (str): Application name for Django registry
        skip_fixtures_if_model_exists (bool): Skip fixtures if models exist
    """

    name = "platforms.defectdojo"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for fixture initialization.

        Returns the DefectDojoSettings model for automatic fixture loading
        during application initialization.

        Returns:
            list[Any]: List containing DefectDojoSettings model class
        """
        from platforms.defectdojo.models import DefectDojoSettings

        return [DefectDojoSettings]

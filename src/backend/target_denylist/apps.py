"""Django application configuration for target denylist module.

Configures the target denylist application with fixture loading support
and model registration for proper integration with Rekono's framework.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class TargetDenylistConfig(BaseApp, AppConfig):
    """Application configuration for target denylist module.

    Extends BaseApp and AppConfig to provide proper Django application
    setup with fixture loading capabilities and model registration.

    Attributes:
        name (str): Application name identifier.
        skip_fixtures_if_model_exists (bool): Skip fixture loading if models exist.
    """

    name = "target_denylist"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get list of models for this application.

        Returns:
            list[Any]: List containing TargetDenylist model class.
        """
        from target_denylist.models import TargetDenylist

        return [TargetDenylist]

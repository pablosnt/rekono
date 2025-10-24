"""Django application configuration for target denylist module.

Configures the target denylist application with fixture loading support
and model registration for proper integration with Rekono's framework.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class TargetDenylistConfig(BaseApp, AppConfig):
    """Application configuration for target denylist module.

    Extends BaseApp and AppConfig to provide proper Django application
    setup with fixture loading capabilities and model registration.

    Attributes:
        name (str): Application name identifier.
        recreate_data (bool): Enable full data recreation during fixture loading.
    """

    name = "target_denylist"
    recreate_data = True

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select user-created denylist entries to preserve during fixture recreation.

        Identifies custom denylist entries created by users (default=False) that
        should be preserved during data recreation to maintain user configurations.

        Args:
            model (Any): The TargetDenylist model class.

        Returns:
            QuerySet: User-created denylist entries to preserve.
        """
        return model.objects.filter(default=False)

    def _get_models(self) -> list[Any]:
        """Get list of models for this application.

        Returns:
            list[Any]: List containing TargetDenylist model class.
        """
        from target_denylist.models import TargetDenylist

        return [TargetDenylist]

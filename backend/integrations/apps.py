"""Django application configuration for integrations module.

Configures the integrations application with custom fixture loading logic
to preserve user-disabled integration states across deployments.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    """Configuration class for the integrations Django application.

    Extends BaseApp to provide custom fixture loading behavior that preserves
    user-configured integration enabled/disabled states across deployments.

    Attributes:
        name (str): The Django application name
    """

    name = "integrations"

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select disabled integrations to preserve during fixture recreation.

        Identifies integrations that have been disabled by users and should
        be preserved with their disabled state during fixture reloading.

        Args:
            model (Any): The Integration model class.

        Returns:
            QuerySet: QuerySet of disabled integration IDs to preserve.
        """
        return model.objects.filter(enabled=False).values_list("id", flat=True)

    def _recreate(self, data: list[Any]) -> None:
        """Re-disable integrations that were previously disabled by users.

        Takes a list of integration IDs that were disabled before fixture
        reloading and ensures they remain disabled after the reload process.

        Args:
            data (list[Any]): List of integration IDs to disable.
        """
        from integrations.models import Integration

        return Integration.objects.filter(id__in=data, enabled=True).update(enabled=False)

    def _get_models(self) -> list[Any]:
        """Get model classes for existence checking during fixture loading.

        Returns:
            list[Any]: List containing the Integration model class.
        """
        from integrations.models import Integration

        return [Integration]

"""Django application configuration for integrations module.

Configures the integrations application with custom fixture loading logic
to preserve user-configured integration enabled states across deployments.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    """Configuration class for the integrations Django application.

    Extends BaseApp to provide custom fixture loading behavior that preserves
    user-configured integration enabled/disabled states, in both directions,
    across deployments and migrations.

    Attributes:
        name (str): The Django application name
    """

    name = "integrations"

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Snapshot the enabled state of every integration before fixture recreation.

        Captures the current enabled/disabled flag of all integrations so that any
        user change, in either direction, survives the fixture reload. The fixture
        hardcodes an enabled value per integration and loaddata restores it on every
        migrate, so the live state must be snapshotted and re-applied afterwards.

        Args:
            model (Any): The Integration model class.

        Returns:
            QuerySet: QuerySet of (id, enabled) tuples for every integration.
        """
        return model.objects.values_list("id", "enabled")

    def _recreate(self, data: list[Any]) -> None:
        """Re-apply the user-configured enabled state after fixture recreation.

        Takes the (id, enabled) snapshot captured before the fixture reload and
        restores it, so integrations the user enabled or disabled keep their state
        even though loaddata reset every record to its fixture default. Integrations
        added to the fixture after the snapshot are left with their default.

        Args:
            data (list[Any]): List of (id, enabled) tuples to restore.
        """
        from integrations.models import Integration

        Integration.objects.filter(id__in=[i for i, enabled in data if enabled], enabled=False).update(enabled=True)
        Integration.objects.filter(id__in=[i for i, enabled in data if not enabled], enabled=True).update(enabled=False)

    def _get_models(self) -> list[Any]:
        """Get model classes for existence checking during fixture loading.

        Returns:
            list[Any]: List containing the Integration model class.
        """
        from integrations.models import Integration

        return [Integration]

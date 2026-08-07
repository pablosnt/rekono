"""Django app configuration of the integrations app."""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    """Configuration of the integrations app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "integrations"

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select which integrations the users have enabled and disabled.

        Args:
            model: The integration model, which is about to be cleared.

        Returns:
            The identifier of each integration with its state, instead of the whole
            entities, since only that state has to survive the reload.
        """
        return model.objects.values_list("id", "enabled")

    def _recreate(self, data: list[Any]) -> None:
        """Enable and disable again the integrations that the users had chosen.

        The fixtures define whether each integration is enabled, and they are
        loaded on every migration, so the choice of the users has to be applied
        again afterwards. The integrations added after the last migration keep
        what the fixtures say about them.

        Args:
            data: Identifier of each integration with its previous state.
        """
        from integrations.models import Integration

        Integration.objects.filter(id__in=[i for i, enabled in data if enabled], enabled=False).update(enabled=True)
        Integration.objects.filter(id__in=[i for i, enabled in data if not enabled], enabled=True).update(enabled=False)

    def _get_models(self) -> list[Any]:
        """Get the integration model, whose data comes from the fixtures.

        Returns:
            The integration model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from integrations.models import Integration

        return [Integration]

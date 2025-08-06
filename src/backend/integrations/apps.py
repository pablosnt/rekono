
from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):

    name = "integrations"

    def load_fixtures(self, **kwargs: Any) -> None:
        from integrations.models import Integration

        # Capture currently disabled integrations before loading fixtures
        disabled_integrations = Integration.objects.filter(enabled=False).values_list("id", flat=True)
        # Load fixtures using parent class method
        super().load_fixtures(**kwargs)
        # Re-disable integrations that were previously disabled by users
        Integration.objects.filter(id__in=disabled_integrations).update(enabled=False)

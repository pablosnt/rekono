from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    name = "integrations"

    def load_fixtures(self, **kwargs: Any) -> None:
        from integrations.models import Integration

        # Keep disabled integrations disabled
        disabled_integrations = Integration.objects.filter(enabled=False).values_list("id", flat=True)
        super().load_fixtures(**kwargs)
        Integration.objects.filter(id__in=disabled_integrations).update(enabled=False)

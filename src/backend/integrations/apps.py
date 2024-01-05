from pathlib import Path
from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class IntegrationsConfig(BaseApp, AppConfig):
    name = "integrations"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"

    def _load_fixtures(self, **kwargs: Any) -> None:
        from integrations.models import Integration

        disabled_integrations = Integration.objects.filter(enabled=False).values_list(
            "id", flat=True
        )
        super()._load_fixtures(**kwargs)
        Integration.objects.filter(id__in=disabled_integrations).update(enabled=False)

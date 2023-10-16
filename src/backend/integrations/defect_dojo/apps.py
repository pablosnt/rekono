from typing import Any

from django.db.models.signals import post_migrate
from framework.apps import BaseApp


class DefectDojoConfig(BaseApp):
    name = "defect_dojo"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self._load_fixtures, sender=self)

    def _load_fixtures(self, **kwargs: Any) -> None:
        from integrations.defect_dojo.models import DefectDojoSettings

        if DefectDojoSettings.objects.exists():
            return
        return super()._load_fixtures(**kwargs)

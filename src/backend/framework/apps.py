from typing import Any

from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class BaseApp:
    fixtures_path = None
    skip_if_model_exists = False

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        if self.fixtures_path:
            post_migrate.connect(self._load_fixtures, sender=self)

    def _load_fixtures(self, **kwargs: Any) -> None:
        if self.fixtures_path:
            if self.skip_if_model_exists:
                for model in self._get_models():
                    if model and model.objects.exists():
                        return  # pragma: no cover
            management.call_command(
                loaddata.Command(),
                *(
                    self.fixtures_path / fixture
                    for fixture in sorted(self.fixtures_path.rglob("*.json"))
                )
            )

    def _get_models(self) -> list[Any]:
        return []  # pragma: no cover

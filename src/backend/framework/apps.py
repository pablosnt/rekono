from pathlib import Path
from typing import Any

from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class BaseApp:
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_fixtures_if_model_exists = False

    def ready(self) -> None:
        # Configure fixtures to be loaded after migration
        if self.fixtures_path:
            post_migrate.connect(self.load_fixtures, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        if self.fixtures_path and self.fixtures_path.is_dir():
            # TODO: Force updates always: Tools
            # TODO: Update default ones, while keeping custom user data: wordlists, processes
            # We will have to handle the custom user data, to remove references to old tools
            if self.skip_fixtures_if_model_exists:
                for model in self._get_models():
                    if model and model.objects.exists():
                        return  # pragma: no cover
            management.call_command(
                loaddata.Command(),
                *(self.fixtures_path / fixture for fixture in sorted(self.fixtures_path.rglob("*.json"))),
            )

    def _get_models(self) -> list[Any]:
        # Models can't be defined in a variable because the first time that the migrate command is executed,
        # models don't exist yet. They only can be imported from a post_migrate signal
        return []  # pragma: no cover

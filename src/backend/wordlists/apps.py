import os
from pathlib import Path
from typing import Any, List

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class WordlistsConfig(BaseApp, AppConfig):
    name = "wordlists"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_if_model_exists = True

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        super().ready()
        post_migrate.connect(self.update_default_wordlists_size, sender=self)

    def _load_fixtures(self, **kwargs: Any) -> None:
        super()._load_fixtures(**kwargs)
        self.update_default_wordlists_size()

    def update_default_wordlists_size(self, **kwargs: Any) -> None:
        """Update default wordlists size."""
        for wordlist in self._get_models()[0].objects.all():
            if Path(wordlist.path).is_file() and os.access(
                wordlist.path, os.R_OK
            ):  # pragma: no cover
                with open(wordlist.path, "rb+") as wordlist_file:
                    wordlist.size = len(wordlist_file.readlines())
                    wordlist.save(update_fields=["size"])

    def _get_models(self) -> List[Any]:
        from wordlists.models import Wordlist

        return [Wordlist]

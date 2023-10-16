import os
from typing import Any

from django.db.models.signals import post_migrate
from framework.apps import BaseApp


class WordlistsConfig(BaseApp):
    name = "wordlists"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self._load_fixtures, sender=self)
        post_migrate.connect(self.update_default_wordlists_size, sender=self)

    def _load_fixtures(self, **kwargs: Any) -> None:
        from wordlists.models import Wordlist

        if Wordlist.objects.exists():
            return
        super()._load_fixtures(**kwargs)
        self.update_default_wordlists_size()

    def update_default_wordlists_size(self, **kwargs: Any) -> None:
        """Update default wordlists size."""
        from wordlists.models import Wordlist

        for wordlist in Wordlist.objects.all():  # For each default wordlist
            if os.path.isfile(wordlist.path) and os.access(wordlist.path, os.R_OK):
                with open(wordlist.path, "rb+") as wordlist_file:  # Open uploaded file
                    wordlist.size = len(wordlist_file.readlines())
                    wordlist.save(update_fields=["size"])

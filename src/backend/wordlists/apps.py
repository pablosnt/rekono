import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class WordlistsConfig(AppConfig):
    name = "wordlists"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self.load_resources_model, sender=self)
        post_migrate.connect(self.update_default_wordlists_size, sender=self)

    def load_resources_model(self, **kwargs: Any) -> None:
        """Load input types fixtures in database."""
        from wordlists.models import Wordlist

        if Wordlist.objects.exists():  # Check if default data is loaded
            return
        path = os.path.join(Path(__file__).resolve().parent, "fixtures")
        management.call_command(
            loaddata.Command(),
            os.path.join(path, "1_wordlists.json"),  # Input type entities
        )
        self.update_default_wordlists_size()

    def update_default_wordlists_size(self, **kwargs: Any) -> None:
        """Update default wordlists size."""
        from wordlists.models import Wordlist

        for wordlist in Wordlist.objects.all():  # For each default wordlist
            if os.path.isfile(wordlist.path) and os.access(wordlist.path, os.R_OK):
                with open(wordlist.path, "rb+") as wordlist_file:  # Open uploaded file
                    wordlist.size = len(wordlist_file.readlines())
                    wordlist.save(update_fields=["size"])

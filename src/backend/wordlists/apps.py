"""Django app configuration for the wordlists module.

Configures the wordlists Django application with automatic wordlist size
calculation and fixture management capabilities.
"""

import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class WordlistsConfig(BaseApp, AppConfig):
    """Configuration class for the wordlists Django application.

    Extends BaseApp to provide automatic wordlist size calculation and fixture
    management. Handles initialization and maintenance of wordlist metadata.

    Attributes:
        name (str): The name of the Django application
        skip_fixtures_if_model_exists (bool): Skip fixture loading if models exist
    """

    name = "wordlists"
    skip_fixtures_if_model_exists = True

    def ready(self) -> None:
        """Initialize the application when Django starts.

        Connects signal handlers for post-migration wordlist size updates.
        """
        super().ready()
        post_migrate.connect(self.update_default_wordlists_size, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load fixtures and update wordlist sizes.

        Args:
            **kwargs (Any): Additional keyword arguments from fixture loading
        """
        super().load_fixtures(**kwargs)
        self.update_default_wordlists_size()

    def update_default_wordlists_size(self, **kwargs: Any) -> None:
        """Update size field for all existing wordlists.

        Calculates and updates the size field for all wordlists by reading
        the actual files and counting lines. Only processes accessible files.

        Args:
            **kwargs (Any): Additional keyword arguments from signal handlers
        """
        for wordlist in self._get_models()[0].objects.all():
            if Path(wordlist.path).is_file() and os.access(wordlist.path, os.R_OK):  # pragma: no cover
                with open(wordlist.path, "rb+") as wordlist_file:
                    wordlist.size = len(wordlist_file.readlines())
                    wordlist.save(update_fields=["size"])

    def _get_models(self) -> list[Any]:
        """Get the models managed by this application.

        Returns:
            list[Any]: List containing the Wordlist model class
        """
        from wordlists.models import Wordlist

        return [Wordlist]

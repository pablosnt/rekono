"""Django app configuration for the wordlists module.

Configures the wordlists Django application with automatic wordlist size
calculation and fixture management capabilities.
"""

import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class WordlistsConfig(BaseApp, AppConfig):
    """Configuration class for the wordlists Django application.

    Extends BaseApp to provide automatic wordlist size calculation and fixture
    management. Handles initialization and maintenance of wordlist metadata.

    Attributes:
        name (str): The name of the Django application
        recreate_data (bool): Enable full data recreation during fixture loading
    """

    name = "wordlists"
    recreate_data = True

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

    def _select_data_to_restore_relationships(self, model: Any) -> QuerySet:
        """Select default wordlists that need relationship restoration.

        Identifies default wordlists (owner is None) that should have
        their task relationships restored after the recreation process.

        Args:
            model (Any): The Wordlist model class.

        Returns:
            QuerySet: Default wordlists with prefetched task relationships.
        """
        return model.objects.filter(owner__isnull=True).prefetch_related("tasks")

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select user-created wordlists to preserve during fixture recreation.

        Identifies custom wordlists created by users (owner is not None) that
        should be preserved with their task relationships during data recreation.

        Args:
            model (Any): The Wordlist model class.

        Returns:
            QuerySet: User wordlists with prefetched task relationships.
        """
        return model.objects.filter(owner__isnull=False).prefetch_related("tasks")

    def _get_current_entity_from_removed_entity(self, model: Any, removed: Any) -> Any:
        """Find the current wordlist that matches a removed wordlist by path.

        Locates the newly created wordlist instance that corresponds to a
        removed wordlist by matching the file path. Note that after re-creation
        database IDs might change.

        Args:
            model (Any): The Wordlist model class.
            removed (Any): The removed wordlist instance.

        Returns:
            Any: The matching wordlist instance, or None if not found.
        """
        return model.objects.filter(path=removed.path).first()

    def update_default_wordlists_size(self, **kwargs: Any) -> None:
        """Update size field for all existing wordlists.

        Calculates and updates the size field for all wordlists by reading
        the actual files and counting lines. Only processes accessible files.

        Args:
            **kwargs (Any): Additional keyword arguments from signal handlers
        """
        from wordlists.models import Wordlist

        for wordlist in Wordlist.objects.all():
            # Check both file existence and read permissions before processing
            # This prevents errors when wordlist files are missing or inaccessible
            if Path(wordlist.path).is_file() and os.access(wordlist.path, os.R_OK):  # pragma: no cover
                # Open in binary mode to handle any file encoding issues reliably
                with open(wordlist.path, "rb") as wordlist_file:
                    # Count lines to determine wordlist size for UI display
                    wordlist.size = len(wordlist_file.readlines())
                    # Use update_fields for efficiency, only updating the size field
                    wordlist.save(update_fields=["size"])

    def _get_models(self) -> list[Any]:
        """Get the models managed by this application.

        Returns:
            list[Any]: List containing the Wordlist model class
        """
        from wordlists.models import Wordlist

        return [Wordlist]

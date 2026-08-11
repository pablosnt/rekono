"""Django app configuration of the wordlists app."""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class WordlistsConfig(BaseApp, AppConfig):
    """Configuration of the wordlists app.

    Attributes:
        name: Name of the app in the Django app registry.
        recreate_data: The default wordlists are reloaded on every migration, so a
          deployment gets the wordlists that each Rekono version defines.
    """

    name = "wordlists"
    recreate_data = True

    def _select_data_to_restore_relationships(self, model: Any) -> QuerySet:
        """Select the default wordlists, to keep the tasks that reference them.

        Args:
            model: The wordlist model, which is about to be cleared.

        Returns:
            The wordlists without owner, with their tasks prefetched.
        """
        return model.objects.filter(owner__isnull=True).prefetch_related("tasks")

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select the wordlists uploaded by the users, with their tasks.

        Args:
            model: The wordlist model, which is about to be cleared.

        Returns:
            The wordlists with an owner, with their tasks prefetched.
        """
        return model.objects.filter(owner__isnull=False).prefetch_related("tasks")

    def _get_current_entity_from_removed_entity(self, model: Any, removed: Any) -> Any:
        """Find the new default wordlist with the same path as a removed one.

        The wordlists are matched by path because the fixtures may assign them a
        different identifier than the one they had.

        Args:
            model: The wordlist model, where the replacement is searched.
            removed: Default wordlist deleted before the reload.

        Returns:
            The new default wordlist, or None if the fixtures no longer define one
            with that path, so the relationship can't be restored.
        """
        return model.objects.filter(path=removed.path).first()

    def _get_models(self) -> list[Any]:
        """Get the wordlist model, whose data comes from the fixtures.

        Returns:
            The wordlist model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from wordlists.models import Wordlist

        return [Wordlist]

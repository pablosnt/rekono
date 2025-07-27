"""This module provides base classes for Django applications."""

from pathlib import Path
from typing import Any

from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class BaseApp:
    """Base class for Django applications with fixture loading capabilities.

    This abstract base class provides functionality for automatically loading
    fixtures after database migrations. It includes configuration options
    for fixture paths and loading behavior.

    Attributes:
        fixtures_path (Path): Path to the fixtures directory.
        skip_fixtures_if_model_exists (bool): Whether to skip loading if models exist.
    """

    fixtures_path = Path(__file__).resolve().parent / "fixtures"
    skip_fixtures_if_model_exists = False

    def ready(self) -> None:
        """Configure the application when Django is ready.

        Sets up the post_migrate signal to automatically load fixtures
        after database migrations are completed.
        """
        # Configure fixtures to be loaded after migration
        if self.fixtures_path and self.fixtures_path.is_dir():
            post_migrate.connect(self.load_fixtures, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load fixtures from the configured fixtures directory.

        Automatically loads all JSON fixtures found in the fixtures_path
        directory. Can be configured to skip loading if models already exist.

        Args:
            **kwargs: Additional arguments from the post_migrate signal.
        """
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
        """Get the models for this application.

        This method should be overridden by subclasses to return the list
        of models that should be checked before loading fixtures.

        Returns:
            List of model classes for this application.
        """
        # Models can't be defined in a variable because the first time that the migrate command is executed,
        # models don't exist yet. They only can be imported from a post_migrate signal
        return []  # pragma: no cover

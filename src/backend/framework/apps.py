"""Django app configuration utilities for Rekono framework.

Provides base app class with automatic fixture loading capabilities
for Django applications in the Rekono platform.
"""

import importlib
from functools import cached_property
from pathlib import Path
from typing import Any

from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class BaseApp:
    """Base Django application configuration with fixture loading capabilities.

    Provides automatic loading of fixture files after database migrations
    for consistent data initialization across Django applications.

    Attributes:
        skip_fixtures_if_model_exists (bool): Whether to skip loading if data exists.
    """

    skip_fixtures_if_model_exists = False

    @cached_property
    def fixtures_path(self) -> Path:
        """Get the path to the application's fixtures directory.

        Dynamically determines the fixtures directory path based on the
        application module location, following Django conventions.

        Returns:
            Path: Absolute path to the fixtures directory for this application.
        """
        module = importlib.import_module(self.__module__)
        return Path(module.__file__).resolve().parent / "fixtures"

    def ready(self) -> None:
        """Configure the application after Django starts.

        Sets up post-migration signal to automatically load fixtures
        if the fixtures directory exists.
        """
        # Configure fixtures to be loaded after migration
        if self.fixtures_path and self.fixtures_path.is_dir():
            post_migrate.connect(self.load_fixtures, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load fixture files into the database.

        Called automatically after migrations to populate the database
        with initial data. Respects skip_fixtures_if_model_exists setting.

        Args:
            **kwargs (Any): Signal arguments from post_migrate.
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
        """Get model classes for existence checking.

        Returns:
            list[Any]: List of model classes to check for existing data.

        Note:
            This method should be overridden by subclasses to return
            the relevant model classes for the application.
        """
        # Models can't be defined in a variable because the first time that the migrate command is executed,
        # models don't exist yet. They only can be imported from a post_migrate signal
        return []  # pragma: no cover

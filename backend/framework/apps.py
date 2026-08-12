"""Base Django app configuration that loads the fixtures of each Rekono app.

The default data of Rekono is created by the migrations, so a deployment gets it once
and keeps whatever its users did with it afterwards. Only the entities that nothing
outside their own app references are left in fixtures, and those are rebuilt from
scratch after every migration, which lets maintainers reorder them freely.
"""

import importlib
from functools import cached_property
from pathlib import Path
from typing import Any

from django.core import management
from django.core.management.commands import loaddata
from django.db import transaction
from django.db.models.signals import post_migrate


class BaseApp:
    """Base app configuration that loads the app fixtures after the migrations.

    The apps whose fixtures replace the data that they already loaded declare it by
    overriding the clearing hook, since the fixture files assign the primary keys and
    a second load would collide with the rows of the first one.
    """

    @cached_property
    def fixtures_path(self) -> Path:
        """The fixtures directory of the app that defines this configuration."""
        # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
        module = importlib.import_module(self.__module__)
        return Path(module.__file__).resolve().parent / "fixtures"

    def ready(self) -> None:
        """Schedule the fixtures of the app to be loaded after each migration."""
        if self.fixtures_path.is_dir():
            post_migrate.connect(self.load_fixtures, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load all the fixture files of the app, ordered by their file name.

        The clearing and the loading share one transaction, so a fixture that can't be
        loaded leaves the data that the previous deployment had.

        Args:
            **kwargs: Arguments sent by the post_migrate signal.
        """
        with transaction.atomic():
            self._clear_before_load()
            management.call_command(loaddata.Command(), *sorted(self.fixtures_path.rglob("*.json")))

    def _clear_before_load(self) -> None:
        """Delete the data that the fixtures create again, before they are loaded.

        Overridden by the apps whose fixtures assign the primary keys of the rows that
        they create, since loading them twice would collide otherwise.
        """
        return None

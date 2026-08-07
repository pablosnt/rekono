"""Django app configuration of the target denylist app."""

from typing import Any

from django.apps import AppConfig
from django.db.models import QuerySet

from framework.apps import BaseApp


class TargetDenylistConfig(BaseApp, AppConfig):
    """Configuration of the target denylist app.

    Attributes:
        name: Name of the app in the Django app registry.
        recreate_data: The default entries are reloaded on every migration, so the
          denylist of a deployment is updated when Rekono adds or removes entries.
    """

    name = "target_denylist"
    recreate_data = True

    def _select_data_to_recreate(self, model: Any) -> QuerySet:
        """Select the entries added by the administrators, to keep them.

        Args:
            model: The denylist model, which is about to be cleared.

        Returns:
            The entries that aren't provided by Rekono, since the default ones are
            loaded again from the fixtures.
        """
        return model.objects.filter(default=False)

    def _get_models(self) -> list[Any]:
        """Get the denylist model, whose data comes from the fixtures.

        Returns:
            The denylist model, imported inside the method because the models
            don't exist yet the first time that the migrations run.
        """
        from target_denylist.models import TargetDenylist

        return [TargetDenylist]

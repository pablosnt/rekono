from django.db.models.signals import post_migrate
from framework.apps import BaseApp


class InputTypesConfig(BaseApp):
    name = "input_types"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self._load_fixtures, sender=self)

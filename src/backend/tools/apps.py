from typing import Any

from django.db.models.signals import post_migrate
from framework.apps import BaseApp


class ToolsConfig(BaseApp):
    """Tool Django application."""

    name = "tools"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self._load_fixtures, sender=self)
        post_migrate.connect(self.update_tools_status, sender=self)

    def update_tools_status(self, **kwargs: Any) -> None:
        from tools.models import Tool

        for tool in Tool.objects.all():
            tool.update_status()

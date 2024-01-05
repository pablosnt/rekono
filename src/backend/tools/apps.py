from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class ToolsConfig(BaseApp, AppConfig):
    """Tool Django application."""

    name = "tools"
    fixtures_path = Path(__file__).resolve().parent / "fixtures"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        super().ready()
        post_migrate.connect(self.update_tools_status, sender=self)

    def update_tools_status(self, **kwargs: Any) -> None:
        from tools.models import Tool

        for tool in Tool.objects.all():
            tool.update_status()

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class ToolsConfig(BaseApp, AppConfig):
    name = "tools"

    def ready(self) -> None:
        super().ready()
        post_migrate.connect(self.update_tools_status, sender=self)

    def update_tools_status(self, **kwargs: Any) -> None:
        from tools.models import Tool

        for tool in Tool.objects.all():
            tool.update_status()

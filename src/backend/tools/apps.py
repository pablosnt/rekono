"""Django app configuration for tools module.

Provides app configuration with automatic tool status updates after
migration completion to ensure tool availability information is current.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class ToolsConfig(BaseApp, AppConfig):
    """Django app configuration for tools module.

    Extends BaseApp and AppConfig to provide tools-specific initialization
    including automatic tool status updates after migrations.

    Attributes:
        name (str): The application name
    """

    name = "tools"

    def ready(self) -> None:
        """Perform application initialization after Django setup.

        Connects the tool status update handler to post-migration signals
        to ensure tool availability information is updated after database changes.
        """
        super().ready()
        post_migrate.connect(self.update_tools_status, sender=self)

    def update_tools_status(self, **kwargs: Any) -> None:
        """Update installation status for all tools after migrations.

        Triggered by post_migrate signal to refresh tool availability
        and version information after database schema changes.

        Args:
            **kwargs (Any): Signal keyword arguments (unused)
        """
        from tools.models import Tool

        for tool in Tool.objects.all():
            tool.update_status()

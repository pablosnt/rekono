"""Django app configuration for tools module.

Provides app configuration with fixture management for tools and their
configurations, plus automatic tool status updates after migration completion
to ensure tool availability information is current.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class ToolsConfig(BaseApp, AppConfig):
    """Django app configuration for tools module.

    Extends BaseApp and AppConfig to provide tools-specific initialization,
    including fixture management for tools and configurations and automatic
    tool status updates after migrations.

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

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load tool fixtures by recreating internal model data.

        Deletes and recreates internal models (Intensity, Argument, Input, Output)
        while preserving Tool and Configuration entities to maintain consistency
        with related entities like Tasks and Processes.

        Args:
            **kwargs (Any): Additional keyword arguments passed from parent method
        """
        from tools.models import Argument, Input, Intensity, Output

        # Tool and Configuration are not re-created here, to keep consistency
        # with other entities like Tasks or Processes that reference them.
        # The "internal" models below only relate to Tool and Configuration,
        # and are sourced only from fixtures, so they are re-created freely,
        # letting maintainers reorder them in the most convenient way.
        for model in [Intensity, Argument, Input, Output]:
            model.objects.all().delete()
        super().load_fixtures(**kwargs)

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

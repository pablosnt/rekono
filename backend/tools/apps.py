"""Django app configuration of the tools app."""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp


class ToolsConfig(BaseApp, AppConfig):
    """Configuration of the tools app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "tools"

    def ready(self) -> None:
        """Prepare the app, checking the installed tools after each migration."""
        super().ready()
        post_migrate.connect(self.update_tools_status, sender=self)

    def load_fixtures(self, **kwargs: Any) -> None:
        """Load the tool fixtures, recreating everything that belongs to a tool.

        Args:
            **kwargs: Arguments sent by the post_migrate signal.
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
        """Check which tools are installed in the system and which version they run.

        Args:
            **kwargs: Arguments sent by the post_migrate signal.
        """
        from tools.models import Tool

        for tool in Tool.objects.all():
            tool.update_status()

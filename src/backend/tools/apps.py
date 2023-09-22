import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class ToolsConfig(AppConfig):
    """Tool Django application."""

    name = "tools"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self.load_tools_models, sender=self)
        post_migrate.connect(self.update_tools_status, sender=self)

    def load_tools_models(self, **kwargs: Any) -> None:
        """Load tools fixtures in database."""
        path = os.path.join(Path(__file__).resolve().parent, "fixtures")
        management.call_command(
            loaddata.Command(),
            os.path.join(path, "1_tools.json"),
            os.path.join(path, "2_intensities.json"),
            os.path.join(path, "3_configurations.json"),
            os.path.join(path, "4_arguments.json"),
            os.path.join(path, "5_inputs.json"),
            os.path.join(path, "6_outputs.json"),
        )

    def update_tools_status(self, **kwargs: Any) -> None:
        from tools.models import Tool

        for tool in Tool.objects.all():
            tool.update_status()

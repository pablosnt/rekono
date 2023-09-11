import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class ProcessesConfig(AppConfig):
    """Processes Django application."""

    name = "processes"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self.load_processes_models, sender=self)

    def load_processes_models(self, **kwargs: Any) -> None:
        """Load processes fixtures in database."""
        from processes.models import Process, Step

        if Process.objects.exists() or Step.objects.exists():
            return
        # Path to fixtures directory
        path = os.path.join(
            Path(__file__).resolve().parent.parent, "processes", "fixtures"
        )
        management.call_command(
            loaddata.Command(),
            os.path.join(path, "1_processes.json"),
            os.path.join(path, "2_steps.json"),
        )

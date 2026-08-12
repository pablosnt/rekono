"""Command that checks which tools are installed in the deployment."""

from typing import Any

from django.core.management.base import BaseCommand

from tools.models import Tool


class Command(BaseCommand):
    """Command that updates the installation status and version of all the tools.

    The tools are installed in the system where the executions run, and they can be
    updated or removed at any time, so this is run on every deployment instead of
    during the migrations, whose database changes don't say anything about the
    tooling available in that system.

    Attributes:
        help: Description of the command shown by the Django help.
    """

    help = "Update the installation status and version of the tools"

    def handle(self, *args: Any, **options: Any) -> None:
        """Check the installation and the version of each tool.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        for tool in Tool.objects.filter(configurations__deprecated=False).distinct():
            tool.update_status()
        self.stdout.write(
            self.style.SUCCESS(
                f"{Tool.objects.filter(is_installed=True, configurations__deprecated=False).distinct().count()} tools are installed in this system"
            )
        )

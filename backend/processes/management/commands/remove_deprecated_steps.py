"""Command that removes the process steps that can't run anymore."""

from typing import Any

from django.core.management.base import BaseCommand

from processes.models import Step


class Command(BaseCommand):
    """Command that removes the steps whose configuration has been deprecated.

    Deprecated configurations are preserved for historical executions, but a step
    referencing one can never run again, so it is removed to avoid leaving dead
    entries in process definitions. This is run on every deployment, once the
    migrations have loaded the fixtures that flag the deprecated configurations and
    recreate the steps of the default processes.

    Attributes:
        help: Description of the command shown by the Django help.
    """

    help = "Remove the process steps whose configuration is deprecated"

    def handle(self, *args: Any, **options: Any) -> None:
        """Remove all the steps that reference a deprecated configuration.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        removed, _ = Step.objects.filter(configuration__deprecated=True).delete()
        self.stdout.write(self.style.SUCCESS(f"{removed} steps with deprecated configurations have been removed"))

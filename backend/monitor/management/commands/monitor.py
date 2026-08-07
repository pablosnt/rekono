"""Command that starts the monitor loop.

It's run on every deployment, since the monitor job only schedules the next one, so
nothing would trigger the first one after an installation or an upgrade.
"""

from typing import Any

from django.core.management.base import BaseCommand

from monitor.queues import MonitorQueue


class Command(BaseCommand):
    """Command that enqueues a monitor job to be run as soon as possible.

    Attributes:
        help: Description of the command shown by the Django help.
    """

    help = "Trigger monitor system"

    def handle(self, *args: Any, **options: Any) -> None:
        """Enqueue the monitor job.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        MonitorQueue().enqueue()

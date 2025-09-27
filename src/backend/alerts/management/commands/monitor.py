"""Management command to trigger the monitor system for alerts.

Defines a Django management command that enqueues a background monitoring
job for the alerts system.
"""

from typing import Any

from django.core.management.base import BaseCommand

from alerts.queues import MonitorQueue


class Command(BaseCommand):
    """Django management command to trigger the monitor system.

    Enqueues a background monitoring job using the MonitorQueue for manual
    monitoring execution or system initialization.
    """

    help = "Trigger monitor system"

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the management command execution.

        Enqueues a monitoring job for the alerts system to check for
        security events or updates.

        Args:
            *args (Any): Positional arguments passed to the command
            **options (Any): Keyword options passed to the command
        """
        MonitorQueue().enqueue()

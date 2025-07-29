"""Management command to trigger the monitor system for alerts.

This module defines a Django management command that enqueues a background
monitoring job for the alerts system.
"""

from typing import Any

from django.core.management.base import BaseCommand

from alerts.queues import MonitorQueue


class Command(BaseCommand):
    """Django management command to trigger the monitor system.

    This command enqueues a background monitoring job using the MonitorQueue.
    """

    help = "Trigger monitor system"

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the management command execution.

        Enqueues a monitoring job for the alerts system.

        Args:
            *args: Positional arguments passed to the command.
            **options: Keyword options passed to the command.
        """
        MonitorQueue().enqueue()

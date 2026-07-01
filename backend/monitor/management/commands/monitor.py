"""Management command to trigger the monitor system.

Defines a Django management command that enqueues a background monitoring
job for immediate execution.
"""

from typing import Any

from django.core.management.base import BaseCommand

from monitor.queues import MonitorQueue


class Command(BaseCommand):
    """Django management command to trigger the monitor system.

    Enqueues a background monitoring job using the MonitorQueue for manual
    monitoring execution or system initialization.
    """

    help = "Trigger monitor system"

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the management command execution.

        Enqueues a monitoring job to refresh trending CVE and EPSS data
        from the configured threat intelligence platforms.

        Args:
            *args (Any): Positional arguments passed to the command
            **options (Any): Keyword options passed to the command
        """
        MonitorQueue().enqueue()

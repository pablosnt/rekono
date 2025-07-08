from typing import Any

from django.core.management.base import BaseCommand

from alerts.queues import MonitorQueue


class Command(BaseCommand):
    help = "Trigger monitor system"

    def handle(self, *args: Any, **options: Any) -> None:
        MonitorQueue().enqueue()

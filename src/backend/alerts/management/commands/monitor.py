from typing import Any

from alerts.queues import MonitorQueue
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Trigger monitor system"

    def handle(self, *args: Any, **options: Any) -> None:
        MonitorQueue().enqueue()

import logging
from datetime import timedelta
from typing import Any

from alerts.models import MonitorSettings
from django.utils import timezone
from django_rq import job
from framework.queues import BaseQueue
from platforms.cvecrowd.integrations import CveCrowd
from rq.job import Job

logger = logging.getLogger()


class MonitorQueue(BaseQueue):
    name = "monitor"

    def enqueue(self, **kwargs: Any) -> Job:
        settings = MonitorSettings.objects.first()
        job = self._get_queue().enqueue(self.consume, on_success=self._scheduled_callback)
        settings.rq_job_id = job.id
        settings.save(update_fields=["rq_job_id"])
        return job

    @staticmethod
    @job("monitor")
    def consume() -> None:
        logger.info("[Monitor] Monitor job has started")
        settings = MonitorSettings.objects.first()
        settings.last_monitor = timezone.now()
        settings.save(update_fields=["last_monitor"])
        for platform in [CveCrowd()]:
            platform.monitor()

    @staticmethod
    def _scheduled_callback(job: Any, connection: Any, *args: Any, **kwargs: Any) -> None:
        settings = MonitorSettings.objects.first()
        instance = MonitorQueue()
        job = instance._get_queue().enqueue_at(
            settings.last_monitor + timedelta(hours=settings.hour_span),
            instance.consume,
            on_success=instance._scheduled_callback,
        )
        settings.rq_job_id = job.id
        settings.save(update_fields=["rq_job_id"])

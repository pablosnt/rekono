"""Background job queues for alert monitoring.

This module contains the queue classes and job functions for handling
background monitoring tasks, including trending vulnerability monitoring.
"""

from datetime import timedelta
from typing import Any

from django.utils import timezone
from django_rq import job
from rq.job import Job

from alerts.models import MonitorSettings
from framework.queues import BaseQueue
from platforms.cvecrowd.integrations import CveCrowd


class MonitorQueue(BaseQueue):
    """Queue for managing monitoring background jobs.

    Handles the scheduling and execution of periodic monitoring tasks
    that check for trending vulnerabilities and security events.

    Attributes:
        name: The name of the monitoring queue
    """

    name = "monitor"

    def enqueue(self, **kwargs: Any) -> Job:
        """Enqueue a monitoring job.

        Creates and schedules a monitoring job.

        Args:
            **kwargs: Additional keyword arguments for job configuration

        Returns:
            The created RQ job instance
        """
        settings = MonitorSettings.objects.first()
        job = self.queue.enqueue(self.consume, on_success=self._scheduled_callback)
        settings.rq_job_id = job.id
        settings.save(update_fields=["rq_job_id"])
        return job

    @staticmethod
    @job("monitor")
    def consume() -> None:
        """Execute the monitoring job.

        Runs the monitoring process, updating the last monitor timestamp
        and checking all configured monitoring platforms for updates.
        """
        BaseQueue.logger.info("[Monitor] Monitor job has started")
        settings = MonitorSettings.objects.first()
        settings.last_monitor = timezone.now()
        settings.save(update_fields=["last_monitor"])
        for platform in [CveCrowd()]:
            platform.monitor()

    @staticmethod
    def _scheduled_callback(job: Any, connection: Any, *args: Any, **kwargs: Any) -> None:
        """Callback function executed after monitoring job completion.

        Schedules the next monitoring job based on the configured hour span
        and updates the monitor settings with the new job ID.

        Args:
            job: The completed RQ job instance
            connection: The RQ connection object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        settings = MonitorSettings.objects.first()
        # Although this is a static method, we instantiate MonitorQueue to access the queue instance.
        # This is necessary because the scheduling API is instance-based.
        self = MonitorQueue()
        # Schedule the next monitoring job to run after the configured hour span.
        # The job will call this same callback upon completion, creating a recurring schedule.
        job = self.queue.enqueue_at(
            settings.last_monitor + timedelta(hours=settings.hour_span),
            self.consume,
            on_success=self._scheduled_callback,
        )
        settings.rq_job_id = job.id
        settings.save(update_fields=["rq_job_id"])

"""Background job queues for alert monitoring.

Queue classes and job functions for handling background monitoring tasks.
Includes trending CVE monitoring, EPSS score updates, and automated job scheduling.
"""

from datetime import timedelta
from typing import Any

from django.utils import timezone
from django_rq import job
from rq.job import Job

from alerts.models import MonitorSettings
from framework.queues import BaseQueue
from platforms.cvecrowd.integrations import CveCrowd
from platforms.first import First


class MonitorQueue(BaseQueue):
    """Queue for managing monitoring background jobs.

    Handles scheduling and execution of periodic monitoring tasks that check
    for trending vulnerabilities, refresh EPSS scores, and process other
    security intelligence updates. Uses RQ for job management with automatic
    rescheduling.

    Attributes:
        name (str): The name of the monitoring queue
    """

    name = "monitor"

    def enqueue(self, **kwargs: Any) -> Job:
        """Enqueue a monitoring job.

        Creates and schedules a monitoring job, updating the settings with
        the new job ID for tracking.

        Args:
            **kwargs (Any): Additional keyword arguments for job configuration

        Returns:
            Job: The created RQ job instance
        """
        settings = MonitorSettings.objects.first()
        job = self.queue.enqueue(self.consume, on_success=self._scheduled_callback)
        self.logger.info("[Monitor] Monitor job has been enqueued")
        settings.rq_job_id = job.id
        settings.save(update_fields=["rq_job_id"])
        return job

    @staticmethod
    @job("monitor")
    def consume() -> None:
        """Execute the monitoring job.

        Runs the monitoring process by updating the last monitor timestamp
        and invoking each configured monitoring platform to refresh their
        security intelligence data (trending CVEs, EPSS scores, etc.).
        """
        BaseQueue.logger.info("[Monitor] Monitor job has started")
        settings = MonitorSettings.objects.first()
        settings.last_monitor = timezone.now()
        settings.save(update_fields=["last_monitor"])
        for platform in [CveCrowd(), First()]:
            platform.monitor()

    @staticmethod
    def _scheduled_callback(job: Any, connection: Any, *args: Any, **kwargs: Any) -> None:
        """Callback function executed after monitoring job completion.

        Automatically schedules the next monitoring job based on the configured
        hour span, creating a self-sustaining monitoring loop.

        Args:
            job (Any): The completed RQ job instance
            connection (Any): The RQ connection object
            *args (Any): Additional positional arguments
            **kwargs (Any): Additional keyword arguments
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

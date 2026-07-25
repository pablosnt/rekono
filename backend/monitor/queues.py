"""Background job queues for automated threat intelligence monitoring.

Queue classes and job functions for handling background monitoring tasks.
Includes trending CVE monitoring, EPSS score updates, and automated job scheduling.
"""

from datetime import timedelta
from typing import Any

from django.utils import timezone
from django_rq import job
from rq.job import Job, JobStatus

from executions.enums import Status
from executions.models import Execution
from executions.queues import ExecutionsQueue
from framework.queues import BaseQueue
from monitor.models import MonitorSettings
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
        the new job ID for tracking. If a scheduled monitoring job already
        exists, no new job is enqueued to avoid running duplicated monitoring
        loops at the same time.

        Args:
            **kwargs (Any): Additional keyword arguments for job configuration

        Returns:
            Job: The created RQ job instance, or the existing scheduled one
        """
        settings = MonitorSettings.objects.first()
        if settings.rq_job_id:
            existing = self.fetch_job(settings.rq_job_id)
            if existing and existing.get_status() in [JobStatus.QUEUED, JobStatus.SCHEDULED, JobStatus.STARTED]:
                self.logger.info(f"[Monitor] A monitor job with ID {existing.id} already exists")
                return existing
            # The tracked job ID is no longer available
            settings.rq_job_id = None
            settings.save(update_fields=["rq_job_id"])
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
        security intelligence data (trending CVEs, EPSS scores, etc.). Finally,
        reconciles executions whose RQ job has disappeared so they are not left
        stuck in a non-terminal status forever.
        """
        BaseQueue.logger.info("[Monitor] Monitor job has started")
        settings = MonitorSettings.objects.first()
        settings.last_monitor = timezone.now()
        settings.save(update_fields=["last_monitor"])
        for platform in [CveCrowd(), First()]:
            platform.monitor()
        # An execution that started and has a job ID but whose job can no longer be
        # fetched was orphaned (e.g. the worker died), so mark it as errored
        for execution in Execution.objects.filter(
            start__isnull=False, rq_job_id__isnull=False, status__in=Status.in_progress()
        ):
            job = ExecutionsQueue().fetch_job(execution.rq_job_id)
            if not job or job.get_status() in [JobStatus.FINISHED, JobStatus.FAILED, JobStatus.STOPPED, JobStatus.CANCELED]:
                BaseQueue.logger.info(f"[Monitor] Moving execution {execution.id} to Error status due to its orphan RQ job")
                execution.error()

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

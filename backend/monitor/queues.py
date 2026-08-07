"""Queue that runs the monitor job.

The monitor job schedules the next one when it finishes, so the loop keeps running
as long as one job completes, and it's the only queue whose jobs aren't triggered
by something that the users do.
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
    """Queue that refreshes the vulnerability data and recovers the lost executions.

    Attributes:
        name: Name of the RQ queue.
    """

    name = "monitor"

    def enqueue(self, **kwargs: Any) -> Job:
        """Enqueue a monitor job to be run as soon as possible.

        Args:
            **kwargs: Not used, since the monitor job takes no arguments.

        Returns:
            The enqueued job, or the one that is already scheduled, since two
            monitor loops running at the same time would duplicate the work.
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
        """Refresh the data of the monitoring platforms and recover the executions."""
        BaseQueue.logger.info("[Monitor] Monitor job has started")
        settings = MonitorSettings.objects.first()
        settings.last_monitor = timezone.now()
        settings.save(update_fields=["last_monitor"])
        for platform in [CveCrowd(), First()]:
            platform.monitor()
        # An execution stuck in a non-terminal status is orphaned once its RQ job is missing
        # or has already reached a terminal state, since neither case will ever move it forward
        for execution in Execution.objects.filter(rq_job_id__isnull=False, status__in=Status.in_progress()):
            job = ExecutionsQueue().fetch_job(execution.rq_job_id)
            if not job or job.get_status() in [
                JobStatus.FINISHED,
                JobStatus.FAILED,
                JobStatus.STOPPED,
                JobStatus.CANCELED,
            ]:
                BaseQueue.logger.info(
                    f"[Monitor] Moving execution {execution.id} to Error status due to its orphan RQ job"
                )
                execution.error()

    @staticmethod
    def _scheduled_callback(job: Any, connection: Any, *args: Any, **kwargs: Any) -> None:
        """Schedule the next monitor job after the configured hours.

        Args:
            job: Monitor job that just finished.
            connection: Redis connection used by RQ to run the callback.
            *args: Not used, accepted for compatibility with the RQ callbacks.
            **kwargs: Not used, accepted for compatibility with the RQ callbacks.
        """
        settings = MonitorSettings.objects.first()
        # The queue is only reachable from an instance, even though the scheduled job is the
        # same static method that this callback belongs to
        self = MonitorQueue()
        job = self.queue.enqueue_at(
            settings.last_monitor + timedelta(hours=settings.hour_span),
            self.consume,
            on_success=self._scheduled_callback,
        )
        settings.rq_job_id = job.id
        settings.save(update_fields=["rq_job_id"])

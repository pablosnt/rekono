import logging

import django_rq
from django.core.exceptions import ValidationError
from django.utils import timezone
from executions.models import Execution
from queues.utils import cancel_and_delete_job, cancel_job
from rq.command import send_stop_job_command

from tasks.enums import Status
from tasks.models import Task

logger = logging.getLogger()                                                    # Rekono logger


def cancel_task(task: Task) -> None:
    '''Cancel task and all his related executions.

    Args:
        task (Task): Task to cancel

    Raises:
        ValidationError: Raised if task can't be cancelled due to his situation
    '''
    if (
        task.status != Status.CANCELLED and                                     # Task status can't be already cancelled
        # Task status can be requested or running or it can be a periodic task
        (task.status in [Status.REQUESTED, Status.RUNNING] or (task.repeat_in and task.repeat_time_unit))
    ):
        if task.rq_job_id:
            # Job Id exists, so it has been enqueued at least one time
            cancel_and_delete_job('tasks-queue', task.rq_job_id)                # Cancel and delete the task job
            logger.info(f'[Task] Task {task.id} has been cancelled')
        # Get all pending executions for this task
        executions = Execution.objects.filter(task=task, status__in=[Status.REQUESTED, Status.RUNNING]).all()
        connection = django_rq.get_connection('executions-queue')               # Get Redis connection
        for execution in executions:                                            # For each execution
            if execution.rq_job_id:                                             # Job Id exists, so it has been enqueued
                if execution.status == Status.RUNNING:                          # Execution is running right now
                    send_stop_job_command(connection, execution.rq_job_id)      # Cancel running job
                else:
                    cancel_job('executions-queue', execution.rq_job_id)         # Cancel pending job
            logger.info(f'[Execution] Execution {execution.id} has been cancelled')
            execution.status = Status.CANCELLED                                 # Set execution status to Cancelled
            execution.end = timezone.now()                                      # Update execution end date
            execution.save(update_fields=['status', 'end'])
        task.status = Status.CANCELLED                                          # Set task status to Cancelled
        task.end = timezone.now()                                               # Update task end date
        task.save(update_fields=['status', 'end'])
    else:
        logger.warning(f'[Task] Task {task.id} can\'t be cancelled')
        raise ValidationError({'id': f'Task {task.id} can\'t be cancelled'})    # Task is not eligible for cancellation

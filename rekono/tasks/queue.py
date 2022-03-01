import logging
from datetime import timedelta
from typing import Any

import django_rq
from django.utils import timezone
from django_rq import job
from processes.executor import executor as processes
from tasks.enums import Status
from tasks.models import Task
from tools.executor import executor as tools

logger = logging.getLogger()                                                    # Rekono logger


def producer(task: Task) -> None:
    '''Enqueue a new task in the tasks queue.

    Args:
        task (Task): Task to enqueue
    '''
    task_queue = django_rq.get_queue('tasks-queue')                             # Get tasks queue
    task.enqueued_at = timezone.now()                                           # Task will be enqueued now by default
    if task.scheduled_at:                                                       # Task scheduled at specific date
        task.enqueued_at = task.scheduled_at                                    # Update enqueued date
        # Enqueue task at specific date
        task_job = task_queue.enqueue_at(task.scheduled_at, consumer, task=task, on_success=scheduled_callback)
        logger.info(f'[Task] Task {task.id} will be enqueued at {task.scheduled_at}')
    elif task.scheduled_in and task.scheduled_time_unit:
        # Task scheduled after specific amount of time
        delay = {task.scheduled_time_unit.lower(): task.scheduled_in}
        task.enqueued_at = timezone.now() + timedelta(**delay)                  # Update enqueued date
        # Enqueue task after specific amount of time
        task_job = task_queue.enqueue_in(timedelta(**delay), consumer, task=task, on_success=scheduled_callback)
        logger.info(f'[Task] Task {task.id} will be enqueued in {task.scheduled_in} {task.scheduled_time_unit}')
    else:                                                                       # Inmediate task
        # Enqueue task
        task_job = task_queue.enqueue(consumer, task=task, on_success=scheduled_callback)
        logger.info(f'[Task] Task {task.id} has been enqueued')
    task.rq_job_id = task_job.id                                                # Save Job Id in task model
    task.save(update_fields=['enqueued_at', 'rq_job_id'])


@job('tasks-queue')
def consumer(task: Task) -> Task:
    '''Consume jobs from tasks queue and processes them.

    Args:
        task (Task): Task associated to the job

    Returns:
        Task: Processed task
    '''
    if task.tool:
        tools.execute(task)                                                     # Tool task
    elif task.process:
        processes.execute(task)                                                 # Process task
    return task


def scheduled_callback(job: Any, connection: Any, result: Task, *args: Any, **kwargs: Any) -> None:
    '''Run code after execution job success. In this case, enqueue again the periodic tasks.

    Args:
        job (Any): Not used.
        connection (Any): Not used.
        result (Task): Previous task execution
    '''
    if result and result.repeat_in and result.repeat_time_unit:                 # Periodic task
        frequency = {result.repeat_time_unit.lower(): result.repeat_in}
        result.enqueued_at = result.enqueued_at + timedelta(**frequency)        # Update enqueued date
        task_queue = django_rq.get_queue('tasks-queue')                         # Get tasks queue
        # Enqueue the task again after the configured time
        task_job = task_queue.enqueue_at(result.enqueued_at, consumer, task=result, on_success=scheduled_callback)
        logger.info(f'[Task] Task {result.id} has been enqueued again')
        result.rq_job_id = task_job.id                                          # Update Job Id in task model
        result.status = Status.REQUESTED                                        # Update task status
        result.save(update_fields=['enqueued_at', 'rq_job_id', 'status'])

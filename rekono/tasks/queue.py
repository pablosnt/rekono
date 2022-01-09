from datetime import timedelta
from typing import Optional

import django_rq
from django.utils import timezone
from django_rq import job
from processes import executor as processes
from rq.job import Job
from tasks.exceptions import InvalidTaskException
from tasks.models import Task
from tools import executor as tools


def producer(task: Task):
    task_queue = django_rq.get_queue('tasks-queue')
    enqueued_at = timezone.now()
    if task.scheduled_at:
        enqueued_at = task.scheduled_at
        task_job = task_queue.enqueue_at(
            task.scheduled_at,
            consumer,
            task=task,
            on_success=scheduled_callback
        )
    elif task.scheduled_in and task.scheduled_time_unit:
        frequency = {task.scheduled_time_unit.name.lower(): task.scheduled_in}
        enqueued_at = timezone.now() + timedelta(**frequency)
        task_job = task_queue.enqueue_in(
            timedelta(**frequency),
            consumer,
            task=task,
            on_success=scheduled_callback
        )
    else:
        task_job = task_queue.enqueue(
            consumer,
            task=task,
            on_success=scheduled_callback
        )
    task.enqueued_at = enqueued_at
    task.rq_job_id = task_job.id
    task.save()


def scheduled_callback(job, connection, result, *args, **kwargs):
    if result:
        if result.repeat_in and result.repeat_time_unit:
            frequency = {result.repeat_time_unit.name.lower(): result.repeat_in}
            enqueued_at = result.enqueued_at + timedelta(**frequency)
            task_queue = django_rq.get_queue('tasks-queue')
            task_job = task_queue.enqueue_at(
                enqueued_at,
                consumer.process_task,
                task=result,
                on_success=scheduled_callback
            )
            result.enqueued_at = enqueued_at
            result.rq_job_id = task_job.id
            result.save()


@job('tasks-queue')
def consumer(task: Task = None) -> tuple:
    if task:
        if task.tool:
            tools.execute(task)
        elif task.process:
            processes.execute(task)
        else:
            raise InvalidTaskException('Invalid task. Process or tool is required')
        return task


def cancel_and_delete_task(job_id: str) -> Job:
    tasks_queue = django_rq.get_queue('tasks-queue')
    task = tasks_queue.fetch_job(job_id)
    if task:
        task.cancel()
        task.delete()
    return task

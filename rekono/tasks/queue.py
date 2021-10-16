import django_rq
from tasks.models import Task
from datetime import timedelta
from rq.job import Job
from tasks.exceptions import InvalidTaskException
from tools import executor as tools
from processes import executor as processes
from django_rq import job


def producer(task: Task, parameters: list, domain: str):
    task_queue = django_rq.get_queue('tasks-queue')
    if task.scheduled_at:
        task_job = task_queue.enqueue_at(
            task.scheduled_at,
            consumer,
            task=task,
            parameters=parameters,
            domain=domain,
            on_success=scheduled_callback
        )
    elif task.scheduled_in and task.scheduled_time_unit:
        frequency = {task.scheduled_time_unit.name.lower(): task.scheduled_in}
        task_job = task_queue.enqueue_in(
            timedelta(**frequency),
            consumer,
            task=task,
            parameters=parameters,
            domain=domain,
            on_success=scheduled_callback
        )
    else:
        task_job = task_queue.enqueue(
            consumer,
            task=task,
            parameters=parameters,
            domain=domain,
            on_success=scheduled_callback
        )
    task.rq_job_id = task_job.id
    task.save()


def scheduled_callback(job, connection, result, *args, **kwargs):
    if result:
        task, parameters, domain = result
        if task.repeat_in and task.repeat_time_unit:
            frequency = {task.repeat_time_unit.name.lower(): task.repeat_in}
            task_queue = django_rq.get_queue('tasks-queue')
            task_job = task_queue.enqueue_in(
                timedelta(**frequency),
                consumer.process_task,
                task=task,
                parameters=parameters,
                domain=domain,
                on_success=scheduled_callback
            )
            task.rq_job_id = task_job.id
            task.save()


@job('tasks-queue')
def consumer(task: Task = None, parameters: list = [], domain: str = None) -> tuple:
    if task:
        if task.tool:
            tools.execute(task, parameters, domain)
        elif task.process:
            processes.execute(task, parameters, domain)
        else:
            raise InvalidTaskException('Invalid task. Process or tool is required')
        return task, parameters, domain


def cancel_and_delete_task(job_id: str) -> Job:
    tasks_queue = django_rq.get_queue('tasks-queue')
    task = tasks_queue.fetch_job(job_id)
    if task:
        task.cancel()
        task.delete()
    return task

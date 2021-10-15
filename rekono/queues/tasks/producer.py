import django_rq
from executions.models import Task
from queues.tasks import consumer
from datetime import timedelta


def process_task(task: Task, parameters: list, domain: str):
    task_queue = django_rq.get_queue('tasks-queue')
    if task.scheduled_at:
        task_job = task_queue.enqueue_at(
            task.scheduled_at,
            consumer.process_task,
            task=task,
            parameters=parameters,
            domain=domain,
            on_success=scheduled_callback
        )
    elif task.scheduled_in and task.scheduled_time_unit:
        frequency = {task.scheduled_time_unit.name.lower(): task.scheduled_in}
        task_job = task_queue.enqueue_in(
            timedelta(**frequency),
            consumer.process_task,
            task=task,
            parameters=parameters,
            domain=domain,
            on_success=scheduled_callback
        )
    else:
        task_job = task_queue.enqueue(
            consumer.process_task,
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

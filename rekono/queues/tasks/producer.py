import django_rq
from executions.models import Task
from queues.tasks import consumer


def process_request(task: Task, parameters: list):
    task_queue = django_rq.get_queue('tasks-queue')
    task_queue.enqueue(consumer.process_request, task=task, parameters=parameters)

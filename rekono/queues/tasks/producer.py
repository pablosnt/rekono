import django_rq
from executions.models import Request
from queues.tasks import consumer


def create_task(request: Request, parameters: list):
    task_queue = django_rq.get_queue('tasks-queue')
    task_queue.enqueue(consumer.run_task, request=request, parameters=parameters)

import django_rq
from executions.models import Request
from queues.requests import consumer


def process_request(request: Request, parameters: list):
    request_queue = django_rq.get_queue('requests-queue')
    request_queue.enqueue(consumer.process_request, request=request, parameters=parameters)

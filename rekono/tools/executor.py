from django.utils import timezone
from executions.models import Execution
from tasks.models import Task
from tools.models import Intensity, Input
from executions.queue import producer


def execute(task: Task, parameters: list, domain: str) -> None:
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    inputs = Input.objects.filter(configuration=task.configuration).all()
    execution = Execution.objects.create(task=task)
    execution.save()
    producer.producer(
        execution=execution,
        intensity=intensity,
        inputs=inputs,
        parameters=parameters,
        domain=domain,
        callback=success_callback
    )


def success_callback(job, connection, result, *args, **kwargs):
    task = result.execution.task
    task.status = result.execution.status
    task.end = timezone.now()
    task.save()

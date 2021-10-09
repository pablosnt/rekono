from django.utils import timezone
from executions.enums import Status
from executions.models import Execution, Task
from tools.models import Intensity, Input
from queues.executions import producer


def execute(task: Task, parameters: list) -> None:
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    inputs = Input.objects.filter(configuration=task.configuration).all()
    task.status = Status.RUNNING
    task.start = timezone.now()
    task.save()
    execution = Execution.objects.create(task=task)
    execution.save()
    producer.execute(
        execution=execution,
        intensity=intensity,
        inputs=inputs,
        parameters=parameters,
        callback=success_callback
    )


def success_callback(job, connection, result, *args, **kwargs):
    task = result.execution.task
    task.status = result.execution.status
    task.end = timezone.now()
    task.save()

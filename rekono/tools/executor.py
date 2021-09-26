from django.utils import timezone
from executions.enums import Status
from executions.models import Execution, Request
from tools.models import Intensity, Input
from queues.executions import producer


def execute(request: Request, parameters: list) -> None:
    intensity = Intensity.objects.filter(tool=request.tool, value=request.intensity).first()
    inputs = Input.objects.filter(configuration=request.configuration).all()
    request.status = Status.RUNNING
    request.start = timezone.now()
    request.save()
    execution = Execution.objects.create(request=request)
    execution.save()
    producer.execute(
        execution=execution,
        intensity=intensity,
        inputs=inputs,
        parameters=parameters,
        callback=success_callback
    )


def success_callback(job, connection, result, *args, **kwargs):
    request = result.execution.request
    request.status = result.execution.status
    request.end = timezone.now()
    request.save()

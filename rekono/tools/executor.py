from django.utils import timezone
from executions.enums import Status
from executions.models import Execution, Request
from tools.models import Intensity
from queues.executions import producer


def execute(request: Request, parameters: list) -> None:
    execution = Execution.objects.create(request=request)
    execution.save()
    intensity = Intensity.objects.filter(
        tool=request.tool,
        value=request.intensity
    ).first()
    request.status = Status.RUNNING
    request.start = timezone.now()
    request.save()
    producer.execute(execution, intensity, parameters, [], success_callback)


def success_callback(job, connection, result, *args, **kwargs):
    request = result.execution.request
    request.status = result.execution.status
    request.end = timezone.now()
    request.save()

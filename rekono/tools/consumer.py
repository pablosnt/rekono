from django.utils import timezone
from executions.enums import Status
from executions.models import Execution, Request
from tools import utils
from tools.models import Configuration, Input, Intensity


def run(request: Request, parameters: list) -> None:
    execution = Execution.objects.create(request=request)
    execution.save()
    configuration = request.configuration
    if not configuration:
        configuration = Configuration.objects.filter(
            tool=request.tool,
            default=True
        )[0]
    inputs = Input.objects.filter(
        configuration=configuration
    )
    intensity = Intensity.objects.filter(
        tool=request.tool,
        value=request.intensity
    )[0]
    tool_class = utils.get_tool_class_by_name(request.tool.name)
    tool = tool_class(
        tool=request.tool,
        configuration=configuration,
        inputs=inputs,
        intensity=intensity
    )
    request.status = Status.RUNNING
    request.start = timezone.now()
    request.save()
    tool.run(
        target=request.target,
        target_ports=request.target.target_ports.all(),
        execution=execution,
        parameters=parameters,
        previous_findings=[]
    )
    request.end = timezone.now()
    request.status = execution.status
    request.save()

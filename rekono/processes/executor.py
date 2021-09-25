from executions.enums import Status
from executions.models import Execution
from executions.models import Request
from processes.models import Step
from tools.enums import FindingType
from tools.models import Input, Intensity, Output
from queues.executions import producer
from django.utils import timezone


class ExecutionJob():

    def __init__(self, step, intensity) -> None:
        self.step = step
        self.intensity = intensity
        self.inputs = Input.objects.filter(configuration=step.configuration).all()
        self.input_types = [o.type for o in self.inputs]
        self.outputs = Output.objects.filter(configuration=step.configuration).all()
        self.output_types = [o.type for o in self.outputs]
        self.job = None
        self.dependencies = set()


def create_plan(request: Request) -> list:
    execution_plan = []
    steps = Step.objects.filter(process=request.process).order_by('tool__stage')
    for step in steps:
        intensity = Intensity.objects.filter(
            tool=step.tool,
            value__lte=request.intensity
        ).order_by('-value').first()
        if intensity:
            j = ExecutionJob(step, intensity)
            for job in execution_plan:
                for output in job.output_types:
                    if (
                        output in j.input_types or
                        FindingType.URL in j.input_types and output in [
                            FindingType.HOST,
                            FindingType.ENUMERATION
                        ]
                    ):
                        j.dependencies.add(job)
        execution_plan.append(j)
    return execution_plan


def execute(request: Request, parameters: list) -> None:
    execution_plan = create_plan(request)
    for job in execution_plan:
        execution = Execution(request=request, step=job.step)
        job.job = producer.execute(
            execution,
            job.intensity,
            job.inputs,
            parameters,
            callback=success_callback,
            dependencies=[j.job for j in job.dependencies]
        )


def success_callback(job, connection, result, *args, **kwargs):
    request = result.execution.request
    pending_executions = Execution.objects.filter(
        request=request,
        status__in=[Status.REQUESTED, Status.RUNNING]
    ).count()
    if pending_executions == 0:
        request.status = result.execution.status
        request.end = timezone.now()
        request.save()

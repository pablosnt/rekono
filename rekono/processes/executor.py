from django.utils import timezone
from tasks.enums import Status
from executions.models import Execution
from tasks.models import Task
from processes.models import Step
from executions.queue import producer
from tools.enums import FindingType
from tools.models import Input, Intensity, Output


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


def create_plan(task: Task) -> list:
    execution_plan = []
    steps = Step.objects.filter(process=task.process).order_by('tool__stage', 'priority')
    for step in steps:
        intensity = Intensity.objects.filter(
            tool=step.tool,
            value__lte=task.intensity
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


def execute(task: Task, parameters: list, domain: str) -> None:
    execution_plan = create_plan(task)
    for job in execution_plan:
        execution = Execution.objects.create(task=task, step=job.step)
        execution.save()
        job.job = producer.producer(
            execution,
            job.intensity,
            job.inputs,
            parameters,
            domain=domain,
            callback=success_callback,
            dependencies=[j.job for j in job.dependencies]
        )


def success_callback(job, connection, result, *args, **kwargs):
    task = result.execution.task
    pending_executions = Execution.objects.filter(
        task=task,
        status__in=[Status.REQUESTED, Status.RUNNING]
    ).count()
    if pending_executions == 0:
        task.status = result.execution.status
        task.end = timezone.now()
        task.save()

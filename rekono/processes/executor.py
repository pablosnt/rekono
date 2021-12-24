from django.utils import timezone
from executions import utils
from executions.models import Execution
from executions.queue import producer
from processes.models import Step
from targets.models import TargetEndpoint
from tasks.enums import Status
from tasks.models import Task
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
        self.jobs = []
        self.dependencies = set()
        self.dependencies_coverage = []


def create_plan(task: Task) -> list:
    execution_plan = []
    steps = Step.objects.filter(process=task.process).order_by('tool__stage', '-priority')
    for step in steps:
        intensity = Intensity.objects.filter(
            tool=step.tool,
            value__lte=task.intensity
        ).order_by('-value').first()
        if intensity:
            j = ExecutionJob(step, intensity)
            for job in execution_plan:
                for output in job.output_types:
                    if output in j.input_types:
                        j.dependencies.add(job)
                        j.dependencies_coverage.append(output)
            execution_plan.append(j)
    return execution_plan


def execute(task: Task, domain: str) -> None:
    execution_plan = create_plan(task)
    for job in execution_plan:
        inputs = [i for i in job.inputs if i.type not in job.dependencies_coverage]
        targets = {
            FindingType.HOST: [task.target],
            FindingType.ENUMERATION: list(task.target.target_ports.all()),
            FindingType.ENDPOINT: list(TargetEndpoint.objects.filter(
                target_port__target=task.target
            ).all()),
            FindingType.WORDLIST: list(task.wordlists.all())
        }
        executions = utils.get_executions_from_findings(targets, inputs)
        for execution_targets in executions:
            execution = Execution.objects.create(task=task, step=job.step)
            execution.save()
            job.jobs.append(
                producer.producer(
                    execution,
                    job.intensity,
                    job.inputs,
                    execution_targets,
                    domain=domain,
                    callback=success_callback,
                    dependencies=[job_id for j in job.dependencies for job_id in j.jobs]
                )
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

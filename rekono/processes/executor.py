from django.utils import timezone
from executions import utils
from executions.models import Execution
from executions.queue import producer
from input_types.models import InputType
from processes.models import Step
from targets.models import TargetEndpoint
from tasks.enums import Status
from tasks.models import Task
from tools.models import Argument, Intensity


class ExecutionJob:

    def __init__(self, step, intensity) -> None:
        self.step = step
        self.intensity = intensity
        self.arguments = Argument.objects.filter(tool=step.tool).all()
        self.inputs = InputType.objects.filter(inputs__argument__tool=step.tool).distinct()
        self.outputs = InputType.objects.filter(
            outputs__configuration=step.configuration
        ).distinct()
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
                for output in job.outputs:
                    if output in j.inputs:
                        j.dependencies.add(job)
                        j.dependencies_coverage.append(output)
            execution_plan.append(j)
    return execution_plan



def execute(task: Task) -> None:
    execution_plan = create_plan(task)
    for job in execution_plan:
        covered_targets = [i.callback_target for i in job.dependencies_coverage if i.callback_target is not None]
        targets = list(task.wordlists.all())
        if 'Target' not in covered_targets:
            targets.append(task.target)
        if 'TargetPort' not in covered_targets:
            targets.extend(list(task.target.target_ports.all()))
        if 'TargetEnumeration' not in covered_targets:
            targets.extend(list(TargetEndpoint.objects.filter(target_port__target=task.target).all()))
        executions = utils.get_executions_from_findings(targets, job.step.tool)
        for execution_targets in executions:
            execution = Execution.objects.create(task=task, step=job.step)
            execution.save()
            job.jobs.append(
                producer.producer(
                    execution,
                    job.intensity,
                    job.arguments,
                    execution_targets,
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

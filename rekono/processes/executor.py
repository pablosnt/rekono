from django.utils import timezone
from executions.models import Execution
from executions.queue import producer
from processes.models import Step
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
                    if output in j.input_types:
                        j.dependencies.add(job)
            execution_plan.append(j)
    return execution_plan


def execute(task: Task, manual_findings: list, domain: str) -> None:
    execution_plan = create_plan(task)
    target_ports = task.target.target_ports.all()
    enumerations = False
    for job in execution_plan:
        if not enumerations and target_ports and job.step.tool.for_each_target_port:
            for tp in target_ports:
                execution = Execution.objects.create(task=task, step=job.step)
                execution.save()
                job.jobs.append(
                    producer.producer(
                        execution,
                        job.intensity,
                        job.inputs,
                        manual_findings,
                        target_ports=[tp],
                        domain=domain,
                        callback=success_callback,
                        dependencies=[job_id for j in job.dependencies for job_id in j.jobs]
                    )
                )
        else:
            execution = Execution.objects.create(task=task, step=job.step)
            execution.save()
            job.jobs.append(
                producer.producer(
                    execution,
                    job.intensity,
                    job.inputs,
                    manual_findings,
                    target_ports=target_ports,
                    domain=domain,
                    callback=success_callback,
                    dependencies=[job_id for j in job.dependencies for job_id in j.jobs]
                )
            )
        if FindingType.ENUMERATION in job.output_types:
            enumerations = True


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

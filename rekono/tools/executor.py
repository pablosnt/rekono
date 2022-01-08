from django.utils import timezone
from executions import utils
from executions.models import Execution
from executions.queue import producer
from inputs.enums import InputTypeNames
from targets.models import TargetEndpoint
from tasks.models import Task
from tools.models import Argument, Intensity


def execute(task: Task) -> None:
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    arguments = Argument.objects.filter(tool=task.tool).all()
    targets = {
        InputTypeNames.HOST: [task.target],
        InputTypeNames.ENUMERATION: list(task.target.target_ports.all()),
        InputTypeNames.ENDPOINT: list(TargetEndpoint.objects.filter(
            target_port__target=task.target
        ).all()),
        InputTypeNames.WORDLIST: list(task.wordlists.all())
    }
    executions = utils.get_executions_from_findings(targets, arguments)
    for execution_targets in executions:
        execution = Execution.objects.create(task=task)
        execution.save()
        producer.producer(
            execution=execution,
            intensity=intensity,
            arguments=arguments,
            targets=execution_targets,
            callback=success_callback
        )


def success_callback(job, connection, result, *args, **kwargs):
    task = result.execution.task
    task.status = result.execution.status
    task.end = timezone.now()
    task.save()

from django.utils import timezone
from executions import utils
from executions.models import Execution
from executions.queue import producer
from input_types.enums import InputTypeNames
from targets.models import TargetEndpoint
from tasks.models import Task
from tools.models import Argument, Intensity


def execute(task: Task) -> None:
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    arguments = Argument.objects.filter(tool=task.tool).all()
    targets = list(task.wordlists.all())
    targets.append(task.target)
    targets.extend(list(task.target.target_ports.all()))
    targets.extend(list(TargetEndpoint.objects.filter(target_port__target=task.target).all()))
    executions = utils.get_executions_from_findings(targets, task.tool)
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

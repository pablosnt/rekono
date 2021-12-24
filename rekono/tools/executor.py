from django.utils import timezone
from executions import utils
from executions.models import Execution
from executions.queue import producer
from targets.models import TargetEndpoint
from tasks.models import Task
from tools.enums import FindingType
from tools.models import Input, Intensity


def execute(task: Task, rekono_address: str) -> None:
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    inputs = Input.objects.filter(configuration=task.configuration).all()
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
        execution = Execution.objects.create(task=task)
        execution.save()
        producer.producer(
            execution=execution,
            intensity=intensity,
            inputs=inputs,
            targets=execution_targets,
            rekono_address=rekono_address,
            callback=success_callback
        )


def success_callback(job, connection, result, *args, **kwargs):
    task = result.execution.task
    task.status = result.execution.status
    task.end = timezone.now()
    task.save()

from django.utils import timezone
from executions.models import Execution
from executions.queue import producer
from tasks.models import Task
from tools.models import Input, Intensity


def execute(task: Task, parameters: list, domain: str) -> None:
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    inputs = Input.objects.filter(configuration=task.configuration).all()
    target_ports = task.target.target_ports.all()
    if target_ports and task.tool.for_each_target_port:
        for tp in target_ports:
            execution = Execution.objects.create(task=task)
            execution.save()
            producer.producer(
                execution=execution,
                intensity=intensity,
                inputs=inputs,
                parameters=parameters,
                target_ports=[tp],
                domain=domain,
                callback=success_callback
            )
    else:
        execution = Execution.objects.create(task=task)
        execution.save()
        producer.producer(
            execution=execution,
            intensity=intensity,
            inputs=inputs,
            parameters=parameters,
            target_ports=target_ports,
            domain=domain,
            callback=success_callback
        )


def success_callback(job, connection, result, *args, **kwargs):
    task = result.execution.task
    task.status = result.execution.status
    task.end = timezone.now()
    task.save()

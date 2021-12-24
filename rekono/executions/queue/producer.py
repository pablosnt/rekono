from typing import Any, Callable

import django_rq
from executions.models import Execution
from executions.queue import consumer
from tools.models import Configuration, Input, Intensity


def producer(
    execution: Execution,
    intensity: Intensity,
    inputs: list,
    targets: list = [],
    previous_findings: list = [],
    rekono_address: str = None,
    callback: Callable = None,
    dependencies: list = [],
    at_front: bool = False
) -> Any:
    if execution.step:
        tool = execution.step.tool
        configuration = execution.step.configuration
        if not configuration:
            configuration = Configuration.objects.filter(tool=tool, default=True).first()
        inputs = Input.objects.filter(configuration=configuration)
    else:
        tool = execution.task.tool
        configuration = execution.task.configuration
    executions_queue = django_rq.get_queue('executions-queue')
    execution_job = executions_queue.enqueue(
        consumer.consumer,
        execution=execution,
        tool=tool,
        configuration=configuration,
        intensity=intensity,
        inputs=inputs,
        targets=targets,
        previous_findings=previous_findings,
        rekono_address=rekono_address,
        on_success=callback,
        result_ttl=7200,
        depends_on=dependencies,
        at_front=at_front
    )
    execution_job.meta['rekono_address'] = rekono_address
    execution_job.meta['execution'] = execution
    execution_job.meta['intensity'] = intensity
    execution_job.meta['inputs'] = inputs
    execution_job.meta['callback'] = callback
    execution_job.meta['targets'] = targets
    execution_job.save_meta()
    execution.rq_job_id = execution_job.id
    execution.save()
    return execution_job

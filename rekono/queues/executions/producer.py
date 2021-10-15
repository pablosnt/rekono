from typing import Callable

import django_rq
from executions.models import Execution
from queues.executions import consumer
from tools.models import Configuration, Input, Intensity


def execute(
    execution: Execution,
    intensity: Intensity,
    inputs: list,
    parameters: list = [],
    previous_findings: list = [],
    domain: str = None,
    callback: Callable = None,
    dependencies: list = [],
    at_front: bool = False
) -> None:
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
        consumer.execute,
        execution=execution,
        tool=tool,
        configuration=configuration,
        intensity=intensity,
        inputs=inputs,
        parameters=parameters,
        previous_findings=previous_findings,
        domain=domain,
        on_success=callback,
        result_ttl=7200,
        depends_on=dependencies,
        at_front=at_front
    )
    execution_job.meta['domain'] = domain
    execution_job.meta['execution'] = execution
    execution_job.meta['intensity'] = intensity
    execution_job.meta['inputs'] = inputs
    execution_job.meta['callback'] = callback
    execution_job.meta['parameters'] = parameters
    execution_job.save_meta()
    execution.rq_job_id = execution_job.id
    execution.save()
    return execution_job

from typing import Any, Callable

import django_rq
from executions.models import Execution
from executions.queue import consumer
from tools.models import Argument, Configuration, Intensity


def producer(
    execution: Execution,
    intensity: Intensity,
    arguments: list,
    targets: list = [],
    previous_findings: list = [],
    callback: Callable = None,
    dependencies: list = [],
    at_front: bool = False
) -> Any:
    if execution.step:
        tool = execution.step.tool
        configuration = execution.step.configuration
        if not configuration:
            configuration = Configuration.objects.filter(tool=tool, default=True).first()
        arguments = Argument.objects.filter(tool=tool)
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
        arguments=arguments,
        targets=targets,
        previous_findings=previous_findings,
        on_success=callback,
        result_ttl=7200,
        depends_on=dependencies,
        at_front=at_front
    )
    execution_job.meta['execution'] = execution
    execution_job.meta['intensity'] = intensity
    execution_job.meta['arguments'] = arguments
    execution_job.meta['callback'] = callback
    execution_job.meta['targets'] = targets
    execution_job.save_meta()
    execution.rq_job_id = execution_job.id
    execution.save()
    return execution_job

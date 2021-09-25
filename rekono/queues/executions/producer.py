from typing import Callable

import django_rq
from executions.models import Execution
from queues.executions import consumer
from rq.job import Job
from tools.models import Configuration, Input, Intensity


def execute(
    execution: Execution,
    intensity: Intensity,
    inputs: list = [],
    parameters: list = [],
    callback: Callable = None,
    dependencies: list = []
) -> None:
    if execution.step:
        tool = execution.step.tool
        configuration = execution.step.configuration
        if not configuration:
            configuration = Configuration.objects.filter(tool=tool, default=True).first()
        inputs = Input.objects.filter(configuration=configuration)
    else:
        tool = execution.request.tool
        configuration = execution.request.configuration
    executions_queue = django_rq.get_queue('executions-queue')
    execution_job = executions_queue.enqueue(
        consumer.execute,
        execution=execution,
        tool=tool,
        configuration=configuration,
        intensity=intensity,
        inputs=inputs,
        parameters=parameters,
        on_success=callback,
        depends_on=dependencies,
        result_ttl=3600 if dependencies else 500
    )
    return execution_job

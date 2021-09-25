import django_rq
from executions.models import Execution
from queues.executions import consumer
from tools.models import Intensity
from typing import Callable


def execute(
    execution: Execution,
    intensity: Intensity,
    parameters: list,
    previous_findings: list,
    callback: Callable
) -> None:
    if execution.step:
        tool = execution.step.tool
        configuration = execution.step.configuration
    else:
        tool = execution.request.tool
        configuration = execution.request.configuration
    executions_queue = django_rq.get_queue('executions-queue')
    executions_queue.enqueue(
        consumer.execute,
        execution=execution,
        tool=tool,
        configuration=configuration,
        intensity=intensity,
        parameters=parameters,
        previous_findings=previous_findings,
        on_success=callback
    )

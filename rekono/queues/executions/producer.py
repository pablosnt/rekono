from typing import Callable

import django_rq
from executions.models import Execution
from queues.executions import consumer
from rq.job import Job
from tools.models import Configuration, Input, Intensity


def execute(
    execution: Execution,
    intensity: Intensity,
    inputs: list,
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
    execution_job = Job.create(
        consumer.execute,
        args=[execution, tool, configuration, intensity, inputs, parameters],
        on_success=callback,
        depends_on=dependencies,
        result_ttl=3600 if dependencies else 500
    )
    execution.rq_job_id = execution_job.id
    execution.save()
    executions_queue = django_rq.get_queue('executions-queue')
    executions_queue.enqueue_job(execution_job)
    return execution_job

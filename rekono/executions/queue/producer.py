import logging
from typing import Callable, List

import django_rq
from executions.models import Execution
from executions.queue import consumer
from input_types.base import BaseInput
from rq.job import Job
from tools.models import Argument, Intensity

logger = logging.getLogger()                                                    # Rekono logger


def producer(
    execution: Execution,
    intensity: Intensity,
    arguments: List[Argument],
    targets: List[BaseInput] = [],
    previous_findings: List[BaseInput] = [],
    callback: Callable = None,
    dependencies: List[Job] = [],
    at_front: bool = False
) -> Job:
    '''Enqueue a new execution in the executions queue.

    Args:
        execution (Execution): Execution to enqueue
        intensity (Intensity): Intensity to apply in the execution
        arguments (List[Argument]): Arguments implied in the execution
        targets (List[BaseInput], optional): Targets and resources to include. Defaults to [].
        previous_findings (List[BaseInput], optional): Findings from previous executions to include. Defaults to [].
        callback (Callable, optional): Function to call after success execution. Defaults to None.
        dependencies (List[Any], optional): Job list whose output is required to perform this execution. Defaults to [].
        at_front (bool, optional): Indicate that the execution should be enqueued at first start. Defaults to False.

    Returns:
        Any: Enqueued job in the executions queue
    '''
    executions_queue = django_rq.get_queue('executions-queue')                  # Get executions queue
    execution_job = executions_queue.enqueue(                                   # Enqueue the Execution job
        consumer.consumer,
        execution=execution,
        intensity=intensity,
        arguments=arguments,
        targets=targets,
        previous_findings=previous_findings,
        on_success=callback,
        # Required to get results from dependent jobs
        result_ttl=7200,
        depends_on=dependencies,
        at_front=at_front
    )
    logger.info(
        f'[Execution] Execution {execution.id} ({execution.tool.name} - '
        f'{execution.configuration.name}) has been enqueued'
    )
    # Save important data in job metadata if it is needed later
    execution_job.meta['execution'] = execution
    execution_job.meta['intensity'] = intensity
    execution_job.meta['arguments'] = arguments
    execution_job.meta['callback'] = callback
    execution_job.meta['targets'] = targets
    execution_job.save_meta()
    execution.rq_job_id = execution_job.id                                      # Save job Id in execution model
    execution.save(update_fields=['rq_job_id'])
    return execution_job

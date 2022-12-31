import logging
from typing import List, cast

import django_rq
from executions import utils
from executions.models import Execution
from executions.queue import producer
from findings.models import Finding
from input_types.models import BaseInput
from processes.executor.callback import process_callback
from queues.utils import cancel_and_delete_job
from rq.job import Job
from rq.registry import DeferredJobRegistry
from tools.models import Argument, Intensity
from tools.tools.base_tool import BaseTool

logger = logging.getLogger()                                                    # Rekono logger


def get_findings_from_dependencies(dependencies: list) -> List[BaseInput]:
    '''Get findings from dependencies.

    Args:
        dependencies (list): Id list of dependency jobs

    Returns:
        List[BaseInput]: Finding list obtained from dependencies
    '''
    executions_queue = django_rq.get_queue('executions-queue')                  # Get execution list
    findings = []
    for dep_id in dependencies:                                                 # For each dependency Id
        dependency = executions_queue.fetch_job(dep_id)                         # Get dependency job
        if not dependency or not dependency.result:
            continue                                                            # No job or results found
        findings.extend(dependency.result.findings)                             # Get findings from result
    return findings


def update_new_dependencies(parent_job: str, new_jobs: list) -> None:
    '''Update on hold jobs dependencies to include new jobs as dependency. Based on the parent job dependents.

    Args:
        parent_job (str): Parent job Id, used to get affected on hold jobs
        new_jobs (list): Id list of new jobs
    '''
    executions_queue = django_rq.get_queue('executions-queue')                  # Get execution list
    registry = DeferredJobRegistry(queue=executions_queue)                      # Get on hold jobs registry
    for job_id in registry.get_job_ids():                                       # For each on hold job
        job_on_hold = executions_queue.fetch_job(job_id)                        # Get on hold job
        # If on hold job is waiting for parent job
        if job_on_hold and parent_job in job_on_hold._dependency_ids:
            dependencies = job_on_hold._dependency_ids                          # Get on hold job original dependencies
            # Include new jobs as on hold job dependency
            dependencies.extend(new_jobs)
            meta = job_on_hold.get_meta()                                       # Get on hold job metadata
            cancel_and_delete_job('executions-queue', job_id)                   # Cancel and delete on hold job
            # Enqueue an on hold job copy with new dependencies
            producer.producer(
                meta['execution'],
                meta['intensity'],
                meta['arguments'],
                targets=meta['targets'],
                callback=meta['callback'],
                dependencies=dependencies
            )


def process_dependencies(
    execution: Execution,
    intensity: Intensity,
    arguments: List[Argument],
    targets: List[BaseInput],
    current_job: Job,
    tool_runner: BaseTool
) -> List[BaseInput]:
    '''Get findings from job dependencies and enqueue new executions if required.

    Args:
        execution (Execution): Execution associated to the current job
        intensity (Intensity): Intensity to apply in the execution
        arguments (List[Argument]): Arguments implied in the execution
        targets (List[BaseInput]): Targets and resources to include in the execution
        current_job (Job): Current job
        tool_runner (BaseTool): Tool instance associated to the tool

    Returns:
        List[Finding]: Finding list to include in the current job execution
    '''
    # Get findings from dependent jobs
    findings = get_findings_from_dependencies(current_job._dependency_ids)
    if not findings:
        logger.info('[Execution] No findings found from dependencies')
        return []                                                               # No findings found
    new_jobs_ids = []
    # Get required executions to include all previous findings
    executions: List[List[BaseInput]] = utils.get_executions_from_findings(findings, execution.tool)
    logger.info(f'[Execution] {len(executions) - 1} new executions from previous findings')
    # Filter executions based on tool arguments
    executions = [
        param_set for param_set in executions if tool_runner.check_arguments(targets, cast(List[Finding], param_set))
    ]
    # For each executions, except first whose findings will be included in the current jobs
    for findings in executions[1:]:
        # Create a new execution entity from the current execution data
        new_execution = Execution.objects.create(
            task=execution.task,
            tool=execution.tool,
            configuration=execution.configuration
        )
        job = producer.producer(                                                # Enqueue the new execution
            new_execution,
            intensity,
            arguments,
            targets=targets,
            previous_findings=findings,                                         # Include the previous findings
            callback=process_callback,
            # At queue start, because it could be a dependency of next jobs
            at_front=True
        )
        new_jobs_ids.append(job.id)                                             # Save new Job Id
    if new_jobs_ids:                                                            # New Jobs has been created
        # Update next jobs dependencies based on current job dependents
        update_new_dependencies(current_job.id, new_jobs_ids)
    # Return first findings list to be used in the current job
    return executions[0] if executions else []

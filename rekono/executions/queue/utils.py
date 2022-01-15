from typing import List

import django_rq
from executions.queue import producer
from input_types.models import BaseInput
from rq.job import Job
from rq.registry import DeferredJobRegistry


def cancel_job(job_id: str) -> Job:
    '''Cancel a job based on his Id.

    Args:
        job_id (str): Job Id to be cancelled

    Returns:
        Job: Cancelled job
    '''
    executions_queue = django_rq.get_queue('executions-queue')                  # Get executions queue
    job = executions_queue.fetch_job(job_id)                                    # Get job to be cancelled by Id
    if job:
        job.cancel()                                                            # Cancel job
    return job


def cancel_and_delete_job(job_id: str) -> Job:
    '''Cancel and delete a job based on hist Id.

    Args:
        job_id (str): Job Id to be cancelled and deleted

    Returns:
        Job: Cancelled and deleted job
    '''
    execution = cancel_job(job_id)                                              # Cancel job
    if execution:
        execution.delete()                                                      # Delete job
    return execution


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


def update_new_dependencies(parent_job: str, new_jobs: list, targets: List[BaseInput]) -> None:
    '''Update on hold jobs dependencies to include new jobs as dependency. Based on the parent job dependents.

    Args:
        parent_job (str): Parent job Id, used to get affected on hold jobs
        new_jobs (list): Id list of new jobs
        targets (List[BaseInput]): Target list. It can include all target types and resources
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
            cancel_and_delete_job(job_id)                                       # Cancel and delete on hold job
            # Enqueue an on hold job copy with new dependencies
            producer.producer(
                meta['execution'],
                meta['intensity'],
                meta['arguments'],
                targets=meta['targets'],
                callback=meta['callback'],
                dependencies=dependencies
            )

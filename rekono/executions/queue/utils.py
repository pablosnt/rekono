import django_rq
from django.apps import apps
from executions.queue import producer
from rq.job import Job
from rq.registry import DeferredJobRegistry


def cancel_execution(job_id: str) -> Job:
    executions_queue = django_rq.get_queue('executions-queue')
    execution = executions_queue.fetch_job(job_id)
    if execution:
        execution.cancel()
    return execution


def cancel_and_delete_execution(job_id: str) -> Job:
    execution = cancel_execution(job_id)
    if execution:
        execution.delete()
    return execution


def get_findings_from_dependencies(dependencies: list) -> list:
    executions_queue = django_rq.get_queue('executions-queue')
    findings = []
    for dep_id in dependencies:
        dependency = executions_queue.fetch_job(dep_id)
        if not dependency or not dependency.result:
            continue
        findings.extend(dependency.result.findings)
    return findings


def update_new_dependencies(parent_job: str, new_jobs: list, targets: list) -> None:
    executions_queue = django_rq.get_queue('executions-queue')
    registry = DeferredJobRegistry(queue=executions_queue)
    for job_id in registry.get_job_ids():
        job_on_hold = executions_queue.fetch_job(job_id)
        if job_on_hold and parent_job in job_on_hold._dependency_ids:
            dependencies = job_on_hold._dependency_ids
            dependencies.extend(new_jobs)
            meta = job_on_hold.get_meta()
            cancel_and_delete_execution(job_id)
            producer.producer(
                meta['execution'],
                meta['intensity'],
                meta['arguments'],
                targets=meta['targets'],
                callback=meta['callback'],
                dependencies=dependencies
            )

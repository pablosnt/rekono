import django_rq
from executions.queue import producer
from executions.queue.constants import finding_relations
from rq.job import Job
from rq.registry import DeferredJobRegistry
from tools import utils


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


def get_findings_from_dependencies(dependencies: list) -> dict:
    executions_queue = django_rq.get_queue('executions-queue')
    findings = {}
    for dep_id in dependencies:
        dependency = executions_queue.fetch_job(dep_id)
        if not dependency or not dependency.result:
            continue
        for input_type in finding_relations.keys():
            input_class = utils.get_finding_class_by_type(input_type)
            input_findings = [f for f in dependency.result.findings if isinstance(f, input_class)]
            for finding in input_findings:
                if input_type in findings:
                    findings[input_type].append(finding)
                else:
                    findings[input_type] = [finding]
    return findings


def update_new_dependencies(parent_job: str, new_jobs: list, manual_findings: list) -> None:
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
                meta['inputs'],
                manual_findings=meta['manual_findings'],
                request=meta['domain'],
                callback=meta['callback'],
                dependencies=dependencies
            )

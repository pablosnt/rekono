import django_rq
from queues.executions import producer
from queues.executions.constants import finding_relations
from rq.registry import DeferredJobRegistry
from tools import utils


def cancel_job(job_id) -> None:
    executions_queue = django_rq.get_queue('executions-queue')
    execution = executions_queue.fetch_job(job_id)
    execution.cancel()


def cancel_and_delete_job(job_id) -> None:
    executions_queue = django_rq.get_queue('executions-queue')
    execution = executions_queue.fetch_job(job_id)
    execution.cancel()
    execution.delete()


def get_findings_from_dependencies(dependencies: list) -> dict:
    executions_queue = django_rq.get_queue('executions-queue')
    findings = {}
    for dep_id in dependencies:
        dependency = executions_queue.fetch_job(dep_id)
        if not dependency or not dependency.result:
            continue
        for input_type in finding_relations.keys():
            input_class = utils.get_finding_class_by_type(input_type)
            filter = [f for f in dependency.result.findings if isinstance(f, input_class)]
            for finding in filter:
                if input_type in findings:
                    findings[input_type].append(finding)
                else:
                    findings[input_type] = [finding]
    return findings


def update_new_dependencies(parent_job: str, new_jobs: list, parameters: list) -> None:
    executions_queue = django_rq.get_queue('executions-queue')
    registry = DeferredJobRegistry(queue=executions_queue)
    for job_id in registry.get_job_ids():
        job_on_hold = executions_queue.fetch_job(job_id)
        if job_on_hold and parent_job in job_on_hold._dependency_ids:
            dependencies = job_on_hold._dependency_ids
            dependencies.extend(new_jobs)
            meta = job_on_hold.get_meta()
            cancel_and_delete_job(job_id)
            producer.execute(
                meta['execution'],
                meta['intensity'],
                meta['inputs'],
                parameters=meta['parameters'],
                callback=meta['callback'],
                dependencies=dependencies
            )

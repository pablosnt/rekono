import rq
from django_rq import job
from processes.executor import success_callback
import django_rq
from rq.job import Job
from rq.registry import DeferredJobRegistry
from executions.models import Execution
from tools.models import Configuration, Intensity, Tool
from queues.executions import producer, utils as queue_utils
from tools import utils as tool_utils


@job('executions-queue')
def execute(
    execution: Execution,
    tool: Tool,
    configuration: Configuration,
    intensity: Intensity,
    inputs: list,
    parameters: list,
    previous_findings: list
) -> None:
    current_job = rq.get_current_job()
    execution.rq_job_id = current_job.id
    execution.save()
    if not previous_findings:
        if current_job._dependency_ids:
            previous_findings = process_dependencies(
                execution,
                intensity,
                inputs,
                parameters,
                current_job
            )
    tool_class = tool_utils.get_tool_class_by_name(tool.name)
    tool = tool_class(
        execution=execution,
        tool=tool,
        configuration=configuration,
        inputs=inputs,
        intensity=intensity
    )
    tool.run(parameters=parameters, previous_findings=previous_findings)
    return tool


def process_dependencies(
    execution: Execution,
    intensity: Intensity,
    inputs: list,
    parameters: list,
    current_job: Job
) -> list:
    findings = queue_utils.get_findings_from_dependencies(current_job._dependency_ids)
    if not findings:
        return []
    new_jobs_ids = []
    jobs = queue_utils.get_jobs_from_findings(findings, inputs)
    for job_counter in jobs.keys():
        if job_counter == 0:
            continue
        execution = Execution.objects.create(request=execution.request, step=execution.step)
        job = producer.execute(
            execution,
            intensity,
            inputs,
            parameters=parameters,
            previous_findings=jobs[job_counter],
            callback=success_callback,
            at_front=True
        )
        new_jobs_ids.append(job.id)
    return jobs[0]

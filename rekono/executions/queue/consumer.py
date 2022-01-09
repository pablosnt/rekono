import rq
from django_rq import job
from executions import utils
from executions.models import Execution
from executions.queue import producer
from executions.queue import utils as queue_utils
from processes.executor import success_callback
from rq.job import Job
from tools import utils as tool_utils
from tools.exceptions import InvalidToolParametersException
from tools.models import Configuration, Intensity, Tool
from tools.tools.base_tool import BaseTool


@job('executions-queue')
def consumer(
    execution: Execution,
    tool: Tool,
    configuration: Configuration,
    intensity: Intensity,
    arguments: list,
    targets: list,
    previous_findings: list
) -> BaseTool:
    current_job = rq.get_current_job()
    tool_class = tool_utils.get_tool_class_by_name(tool.name)
    tool_runner = tool_class(
        execution=execution,
        tool=tool,
        configuration=configuration,
        arguments=arguments,
        intensity=intensity
    )
    if not previous_findings and current_job._dependency_ids:
        previous_findings = process_dependencies(
            execution,
            tool,
            intensity,
            arguments,
            targets,
            current_job,
            tool_runner
        )
    tool_runner.run(targets=targets, previous_findings=previous_findings)
    return tool_runner


def process_dependencies(
    execution: Execution,
    tool: Tool,
    intensity: Intensity,
    arguments: list,
    targets: list,
    current_job: Job,
    tool_runner: BaseTool
) -> list:
    findings = queue_utils.get_findings_from_dependencies(current_job._dependency_ids)
    if not findings:
        return []
    new_jobs_ids = []
    all_params = utils.get_executions_from_findings(findings, tool)
    all_params = [
        param_set for param_set in all_params if check_params_for_tool(
            tool_runner, targets, param_set
        )
    ]
    for param_set in all_params[1:]:
        new_execution = Execution.objects.create(task=execution.task, step=execution.step)
        new_execution.save()
        job = producer.producer(
            new_execution,
            intensity,
            arguments,
            targets=targets,
            previous_findings=param_set,
            callback=success_callback,
            at_front=True
        )
        new_jobs_ids.append(job.id)
    if new_jobs_ids:
        queue_utils.update_new_dependencies(current_job.id, new_jobs_ids, targets)
    return all_params[0] if all_params else []


def check_params_for_tool(tool: BaseTool, targets: list, findings: list) -> bool:
    try:
        tool.get_arguments(targets, findings)
        return True
    except InvalidToolParametersException:
        return False

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
    inputs: list,
    targets: list,
    previous_findings: list,
    rekono_address: str,
) -> BaseTool:
    current_job = rq.get_current_job()
    tool_class = tool_utils.get_tool_class_by_name(tool.name)
    tool = tool_class(
        execution=execution,
        tool=tool,
        configuration=configuration,
        inputs=inputs,
        intensity=intensity
    )
    if not previous_findings and current_job._dependency_ids:
        previous_findings = process_dependencies(
            execution,
            intensity,
            inputs,
            targets,
            rekono_address,
            current_job,
            tool
        )
    tool.run(targets=targets, previous_findings=previous_findings, rekono_address=rekono_address)
    return tool


def process_dependencies(
    execution: Execution,
    intensity: Intensity,
    inputs: list,
    targets: list,
    rekono_address: str,
    current_job: Job,
    tool: BaseTool
) -> list:
    findings = queue_utils.get_findings_from_dependencies(current_job._dependency_ids)
    if not findings:
        return []
    new_jobs_ids = []
    all_params = utils.get_executions_from_findings(findings, inputs)
    all_params = [
        param_set for param_set in all_params if check_params_for_tool(tool, targets, param_set)
    ]
    for param_set in all_params[1:]:
        new_execution = Execution.objects.create(task=execution.task, step=execution.step)
        new_execution.save()
        job = producer.producer(
            new_execution,
            intensity,
            inputs,
            targets=targets,
            previous_findings=param_set,
            rekono_address=rekono_address,
            callback=success_callback,
            at_front=True
        )
        new_jobs_ids.append(job.id)
    queue_utils.update_new_dependencies(current_job.id, new_jobs_ids, targets)
    return next(iter(all_params), [])


def check_params_for_tool(tool: BaseTool, targets: list, findings: list) -> bool:
    try:
        tool.get_arguments(targets, findings)
        return True
    except InvalidToolParametersException:
        return False

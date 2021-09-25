from django_rq import job
from executions.models import Execution
from tools import utils
from tools.models import Configuration, Intensity, Tool
import rq
import django_rq


@job('executions-queue')
def execute(
    execution: Execution,
    tool: Tool,
    configuration: Configuration,
    intensity: Intensity,
    inputs: list,
    parameters: list
) -> None:
    current_job = rq.get_current_job()
    previous_findings = process_dependencies(current_job._dependency_ids)
    tool_class = utils.get_tool_class_by_name(tool.name)
    tool = tool_class(
        execution=execution,
        tool=tool,
        configuration=configuration,
        inputs=inputs,
        intensity=intensity
    )
    tool.run(parameters=parameters, previous_findings=previous_findings)
    return tool


def process_dependencies(dependencies: list) -> list:
    previous_findings = []
    executions_queue = django_rq.get_queue('executions-queue')
    for dependency in dependencies:
        d = executions_queue.fetch_job(dependency)
        previous_findings.extend(d.result.findings)
    return previous_findings

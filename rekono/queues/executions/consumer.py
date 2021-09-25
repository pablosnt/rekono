from django_rq import job
from executions.models import Execution
from tools import utils
from tools.models import Configuration, Input, Intensity, Tool


@job('executions-queue')
def execute(
    execution: Execution,
    tool: Tool,
    configuration: Configuration,
    intensity: Intensity,
    parameters: list,
    previous_findings: list
) -> None:
    if not configuration:
        configuration = Configuration.objects.filter(tool=tool, defatul=True).first()
    inputs = Input.objects.filter(configuration=configuration)
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

from typing import List

import rq
from django_rq import job
from executions.models import Execution
from executions.queue import utils as queue_utils
from input_types.base import BaseInput
from tools import utils as tool_utils
from tools.models import Argument, Configuration, Intensity, Tool
from tools.tools.base_tool import BaseTool


@job('executions-queue')
def consumer(
    execution: Execution,
    tool: Tool,
    configuration: Configuration,
    intensity: Intensity,
    arguments: List[Argument],
    targets: List[BaseInput],
    previous_findings: List[BaseInput]
) -> BaseTool:
    '''Consume jobs from executions queue and executes them.

    Args:
        execution (Execution): Execution associated to the job
        tool (Tool): Tool to execute
        configuration (Configuration): Configuration to apply in the execution
        intensity (Intensity): Intensity to apply in the execution
        arguments (List[Argument]): Arguments implied in the execution
        targets (List[BaseInput]): Targets and resources to include in the execution
        previous_findings (List[Finding]): Findings from previous executions to include in the execution

    Returns:
        BaseTool: Tool instance that executed the tool and saved the results
    '''
    tool_class = tool_utils.get_tool_class_by_name(tool.name)                   # Get Tool class from Tool name
    tool_runner = tool_class(                                                   # Create Tool instance
        execution=execution,
        tool=tool,
        configuration=configuration,
        arguments=arguments,
        intensity=intensity
    )
    current_job = rq.get_current_job()                                          # Get current Job
    if not previous_findings and current_job._dependency_ids:                   # No previous findings and dependencies
        previous_findings = queue_utils.process_dependencies(                   # Get findings from dependencies
            execution,
            tool,
            intensity,
            arguments,
            targets,
            current_job,
            tool_runner
        )
    tool_runner.run(targets=targets, previous_findings=previous_findings)       # Tool execution
    return tool_runner

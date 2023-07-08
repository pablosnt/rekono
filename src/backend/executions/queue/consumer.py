from typing import List

import rq
from django.utils import timezone
from django_rq import job
from executions.models import Execution
from executions.queue import utils as queue_utils
from input_types.base import BaseInput
from tasks.enums import Status
from tools import utils as tool_utils
from tools.models import Argument, Intensity
from tools.tools.base_tool import BaseTool


@job('executions-queue')
def consumer(
    execution: Execution,
    intensity: Intensity,
    arguments: List[Argument],
    targets: List[BaseInput],
    previous_findings: List[BaseInput]
) -> BaseTool:
    '''Consume jobs from executions queue and executes them.

    Args:
        execution (Execution): Execution associated to the job
        intensity (Intensity): Intensity to apply in the execution
        arguments (List[Argument]): Arguments implied in the execution
        targets (List[BaseInput]): Targets and resources to include in the execution
        previous_findings (List[Finding]): Findings from previous executions to include in the execution

    Returns:
        BaseTool: Tool instance that executed the tool and saved the results
    '''
    tool_class = tool_utils.get_tool_class_by_name(execution.tool.name)         # Get Tool class from Tool name
    tool_runner = tool_class(execution, intensity, arguments)                   # Create Tool instance
    current_job = rq.get_current_job()                                          # Get current Job
    if not previous_findings and current_job._dependency_ids:                   # No previous findings and dependencies
        previous_findings = queue_utils.process_dependencies(                   # Get findings from dependencies
            execution,
            intensity,
            arguments,
            targets,
            current_job,
            tool_runner
        )
    # If related task start date is null
    # It could be established before, if this execution belongs to a process execution
    if not execution.task.start:
        execution.task.status = Status.RUNNING                                  # Set task status to Running
        execution.task.start = timezone.now()                                   # Set task start date
        execution.task.save(update_fields=['status', 'start'])
    tool_runner.run(targets=targets, previous_findings=previous_findings)       # Tool execution
    return tool_runner

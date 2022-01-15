from typing import List

import rq
from django_rq import job
from executions import utils
from executions.models import Execution
from executions.queue import producer
from executions.queue import utils as queue_utils
from input_types.base import BaseInput
from processes.executor import success_callback
from rq.job import Job
from tools import utils as tool_utils
from tools.exceptions import InvalidToolParametersException
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
        previous_findings = process_dependencies(                               # Get findings from dependencies
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


def process_dependencies(
    execution: Execution,
    tool: Tool,
    intensity: Intensity,
    arguments: List[Argument],
    targets: List[BaseInput],
    current_job: Job,
    tool_runner: BaseTool
) -> List[BaseInput]:
    '''Get findings from job dependencies and enqueue new executions if required.

    Args:
        execution (Execution): Execution associated to the current job
        tool (Tool): Tool to execute
        intensity (Intensity): Intensity to apply in the execution
        arguments (List[Argument]): Arguments implied in the execution
        targets (List[BaseInput]): Targets and resources to include in the execution
        current_job (Job): Current job
        tool_runner (BaseTool): Tool instance associated to the tool

    Returns:
        List[Finding]: Finding list to include in the current job execution
    '''
    # Get findings from dependent jobs
    findings = queue_utils.get_findings_from_dependencies(current_job._dependency_ids)
    if not findings:
        return []                                                               # No findings found
    new_jobs_ids = []
    # Get required executions to include all previous findings
    executions: List[List[BaseInput]] = utils.get_executions_from_findings(findings, tool)
    # Filter executions based on tool arguments
    executions = [param_set for param_set in executions if check_arguments_for_tool(tool_runner, targets, param_set)]
    # For each executions, except first whose findings will be included in the current jobs
    for findings in executions[1:]:
        # Create a new execution entity from the current execution data
        new_execution = Execution.objects.create(task=execution.task, step=execution.step)
        new_execution.save()
        job = producer.producer(                                                # Enqueue the new execution
            new_execution,
            intensity,
            arguments,
            targets=targets,
            previous_findings=findings,                                         # Include the previous findings
            callback=success_callback,
            # At queue start, because it could be a dependency of next jobs
            at_front=True
        )
        new_jobs_ids.append(job.id)                                             # Save new Job Id
    if new_jobs_ids:                                                            # New Jobs has been created
        # Update next jobs dependencies based on current job dependents
        queue_utils.update_new_dependencies(current_job.id, new_jobs_ids, targets)
    # Return first findings list to be used in the current job
    return executions[0] if executions else []


def check_arguments_for_tool(tool: BaseTool, targets: List[BaseInput], findings: List[BaseInput]) -> bool:
    '''Check if given resources (targets, resources and findings) lists are enough to execute a given tool.

    Args:
        tool (BaseTool): Tool instance to be executed
        targets (List[BaseInput]): Target list to include in the tool arguments. It can include targets and resources
        findings (List[BaseInput]): Finding list to include in the tool arguments

    Returns:
        bool: Indicate if the tool can be executed with the given targets and findings
    '''
    try:
        tool.get_arguments(targets, findings)                                   # Try to configure the tool arguments
        return True
    except InvalidToolParametersException:
        return False

import logging

from executions import utils
from executions.models import Execution
from executions.queue import producer
from parameters.models import InputTechnology, InputVulnerability
from tasks.models import Task
from tools.executor.callback import tool_callback
from tools.models import Argument, Intensity

logger = logging.getLogger()                                                    # Rekono logger


def execute(task: Task) -> None:
    '''Execute a task that requests a tool execution.

    Args:
        task (Task): Task that requests a tool execution
    '''
    # Get requested intensity entity
    intensity = Intensity.objects.filter(tool=task.tool, value=task.intensity).first()
    arguments = Argument.objects.filter(tool=task.tool).all()                   # Get arguments for requested tool
    targets = list(task.wordlists.all())                                        # Wordlists are included in targets
    targets.append(task.target)                                                 # Add target to task targets
    targets.extend(list(task.target.target_ports.all()))                        # Add target ports to task targets
    # Add input technologies to task targets
    targets.extend(list(InputTechnology.objects.filter(target=task.target).all()))
    # Add input vulnerabilities to task targets
    targets.extend(list(InputVulnerability.objects.filter(target=task.target).all()))
    # Get the executions required for this job based on targets and tool arguments.
    # A job can need multiple executions. For example, if the user includes more than one Wordlist and
    # the tool is Dirsearch that only accepts one wordlist as argument. Rekono will
    # generate one Dirsearch execution for each wordlist provided by the user. It can also occur with
    # TargetPort, InputTechnology or InputVulnerability.
    executions = utils.get_executions_from_findings(targets, task.tool)
    logger.info(f'[Tool] Task {task.id} requires {len(executions)} executions')
    for execution_targets in executions:                                        # For each job execution
        # Create the Execution entity
        execution = Execution.objects.create(task=task, tool=task.tool, configuration=task.configuration)
        # Enqueue the execution in the executions queue
        producer.producer(
            execution=execution,
            intensity=intensity,
            arguments=arguments,
            targets=execution_targets,
            callback=tool_callback
        )

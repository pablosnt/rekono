from typing import Any, List, Set

from django.utils import timezone
from executions import utils
from executions.models import Execution
from executions.queue import producer
from input_types.models import InputType
from processes.models import Step
from rq.job import Job
from targets.models import TargetEndpoint
from tasks.enums import Status
from tasks.models import Task
from tools.models import Argument, Intensity
from tools.tools.base_tool import BaseTool


class ExecutionJob:
    '''Represents an execution job that will be enqueued in executions queue.'''

    def __init__(self, step: Step, intensity: Intensity) -> None:
        '''Job constructor.

        Args:
            step (Step): Process step to be executed
            intensity (Intensity): Tool intensity to be applied in the execution
        '''
        self.step = step                                                        # Process step to be executed
        self.intensity = intensity                                              # Intensity that will be applied
        self.arguments = Argument.objects.filter(tool=step.tool).all()          # Get implicated arguments
        self.inputs = InputType.objects.filter(inputs__argument__tool=step.tool).distinct()     # Get implicated inputs
        # Get implicated outputs
        self.outputs = InputType.objects.filter(outputs__configuration=step.configuration).distinct()
        # Save the related executions queue jobs. Initialized to empty
        self.jobs: List[Job] = []
        # Save previous executions queue jobs whose output will be needed to execute this job. Initialized to empty
        self.dependencies: Set[Job] = set()
        # Save the Input Types that will be obtained from dependencies
        self.dependencies_coverage: List[InputType] = []


def create_plan(task: Task) -> List[ExecutionJob]:
    '''Create an execution plan for a task that requests a process execution.

    Args:
        task (Task): Task that requests a process execution

    Returns:
        List[ExecutionJob]: List of jobs that should be executed
    '''
    execution_plan: List[ExecutionJob] = []                                     # Execution plan initialized to empty
    # Get all process steps sort by stage and priority (descendent), so steps from previous steps and
    # with greater priority will be included before in the plan
    steps = Step.objects.filter(process=task.process).order_by('tool__stage', '-priority')
    for step in steps:                                                          # For each step
        # Get the greater intensity for this tool, limited to the task intensity
        # If no intensity found with lower value than the task intensity, the step will be skipped
        intensity = Intensity.objects.filter(tool=step.tool, value__lte=task.intensity).order_by('-value').first()
        if intensity:                                                           # Intensity found
            j = ExecutionJob(step, intensity)                                   # Execution job initialization
            for job in execution_plan:                                          # For each planned job (previous jobs)
                for output in job.outputs:                                      # For each previous job output
                    # If output type is in current step input types
                    if output in j.inputs:
                        # Add previous job as current job dependency
                        j.dependencies.add(job)
                        # Add output as dependency covered input type
                        j.dependencies_coverage.append(output)
            execution_plan.append(j)                                            # Add the job to the execution plan
    return execution_plan


def execute(task: Task) -> None:
    '''Execute a task that requests a process execution.

    Args:
        task (Task): Task that requests a process execution
    '''
    execution_plan = create_plan(task)                                          # Create the execution plan
    for job in execution_plan:                                                  # For each planned jobs
        # Check unneeded target types, due to dependencies with previous jobs
        covered_targets = [i.callback_target for i in job.dependencies_coverage if i.callback_target is not None]
        # Wordlist never will be covered by dependencies, so they are included directly in targets
        targets = list(task.wordlists.all())
        if 'Target' not in covered_targets:                                     # Target is not covered by dependencies
            targets.append(task.target)                                         # Add task target to targets
        if 'TargetPort' not in covered_targets:
            # TargetPort is not covered by dependencies
            targets.extend(list(task.target.target_ports.all()))                # Add task target ports to targets
        if 'TargetEndpoint' not in covered_targets:
            # TargetEndpoint is not covered by dependencies
            # Add task target endpoints to targets
            targets.extend(list(TargetEndpoint.objects.filter(target_port__target=task.target).all()))
        # Get the executions required for this job based on targets and tool arguments.
        # A job can need multiple executions. For example, if the user includes more than one Wordlist and
        # the process includes Dirsearch execution that only accepts one wordlist as argument. Rekono will
        # generate one Dirsearch execution for each wordlist provided by the user. It can also occur with
        # TargetPort and TargetEndpoint.
        executions = utils.get_executions_from_findings(targets, job.step.tool)
        for execution_targets in executions:                                    # For each job execution
            execution = Execution.objects.create(task=task, step=job.step)      # Create the Execution object
            execution.save()
            # Enqueue the execution in the executions queue, and save the generated job in the planned job.
            # It's important to get dependency jobs in the next planned jobs
            job.jobs.append(
                producer.producer(
                    execution,
                    job.intensity,
                    job.arguments,
                    execution_targets,
                    callback=success_callback,
                    # Set job dependencies from plan
                    dependencies=[job_id for j in job.dependencies for job_id in j.jobs]
                )
            )


def success_callback(job: Any, connection: Any, result: BaseTool, *args, **kwargs) -> None:
    '''Run code after execution job success. In this case, check if all executions of the same task has been finished.

    Args:
        job (Any): Not used.
        connection (Any): Not used.
        result (BaseTool): Successful execution job result
    '''
    task = result.execution.task                                                # Get the associated task
    # Check if there are pending executions (requested or running) associated to this task
    pending_executions = Execution.objects.filter(task=task, status__in=[Status.REQUESTED, Status.RUNNING]).exists()
    if bool(pending_executions):                                                # No pending executions found
        # Check if there are error executions associated to this task
        error_executions = Execution.objects.filter(task=task, status=Status.ERROR).exists()
        # Set task status to error if error executions found, otherwise to completed
        task.status = Status.COMPLETED if not bool(error_executions) else Status.ERROR
        task.end = timezone.now()                                               # Update the task end date
        task.save(update_fields=['status', 'end'])

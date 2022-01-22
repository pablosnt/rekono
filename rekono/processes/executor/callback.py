from typing import Any

from django.utils import timezone
from executions.models import Execution
from tasks.enums import Status
from tools.tools.base_tool import BaseTool


def process_callback(job: Any, connection: Any, result: BaseTool, *args: Any, **kwargs: Any) -> None:
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
        # Set task status to error if error executions found, completed otherwise
        task.status = Status.COMPLETED if not bool(error_executions) else Status.ERROR
        task.end = timezone.now()                                               # Update the task end date
        task.save(update_fields=['status', 'end'])

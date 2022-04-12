import logging
from typing import Any

from django.utils import timezone
from executions.models import Execution
from tasks.enums import Status
from tools.tools.base_tool import BaseTool

logger = logging.getLogger()                                                    # Rekono logger


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
    if not bool(pending_executions):                                            # No pending executions found
        # Check if there are error executions associated to this task
        error_executions = Execution.objects.filter(task=task, status=Status.ERROR).exists()
        # Check if there are cancelled executions associated to this task
        cancelled_executions = Execution.objects.filter(task=task, status=Status.CANCELLED).exists()
        # Set task status to error if error executions found, completed otherwise
        task_status = Status.COMPLETED if not bool(error_executions) else Status.ERROR
        # Set task status to cancelled if cancelled executions found
        task.status = task_status if not bool(cancelled_executions) else Status.CANCELLED
        task.end = timezone.now()                                               # Update the task end date
        task.save(update_fields=['status', 'end'])
        logger.info(f'[Task] Task {task.id} has been completed with {task.status} status')

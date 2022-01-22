from typing import Any

from django.utils import timezone
from tools.tools.base_tool import BaseTool


def tool_callback(job: Any, connection: Any, result: BaseTool, *args: Any, **kwargs: Any) -> None:
    '''Run code after execution job success. In this case, update task information.

    Args:
        job (Any): Not used.
        connection (Any): Not used.
        result (BaseTool): Successful execution job result
    '''
    task = result.execution.task                                                # Get task associated to the execution
    task.status = result.execution.status                                       # Update task status
    task.end = timezone.now()                                                   # Update the task end date
    task.save(update_fields=['status', 'end'])

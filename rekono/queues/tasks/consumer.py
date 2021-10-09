from executions.models import Task
from executions.exceptions import InvalidTaskException
from tools import executor as tools
from processes import executor as processes
from django_rq import job


@job('requests-queue')
def process_request(task: Task = None, parameters: list = []) -> None:
    if task:
        if task.tool:
            tools.execute(task, parameters)
        elif task.process:
            processes.execute(task, parameters)
        else:
            raise InvalidTaskException('Invalid task. Process or tool is required')

from executions.models import Task
from executions.exceptions import InvalidTaskException
from tools import executor as tools
from processes import executor as processes
from django_rq import job


@job('tasks-queue')
def process_task(task: Task = None, parameters: list = [], domain: str = None) -> tuple:
    if task:
        if task.tool:
            tools.execute(task, parameters, domain)
        elif task.process:
            processes.execute(task, parameters, domain)
        else:
            raise InvalidTaskException('Invalid task. Process or tool is required')
        return task, parameters, domain

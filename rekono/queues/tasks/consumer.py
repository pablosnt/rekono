from executions.models import Request
from executions.exceptions import InvalidRequestException
from tools import executor as tools
from processes import executor as processes
from django_rq import job


@job('tasks-queue')
def run_task(request: Request = None, parameters: list = []) -> None:
    if request:
        if request.tool:
            tools.run(request, parameters)
        elif request.process:
            processes.run(request, parameters)
        else:
            raise InvalidRequestException('Invalid request. Process or tool is required')

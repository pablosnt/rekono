from executions.models import Request
from executions.exceptions import InvalidRequestException
from tools import consumer as tools
from processes import consumer as processes
from django_rq import job


@job('task-queue')
def run_task(request: Request = None, parameters: list = []) -> None:
    if request:
        if request.process:
            processes.run(request, parameters)
        elif request.tool:
            tools.run(request, parameters)
        else:
            raise InvalidRequestException(
                'Invalid request. Process or tool is required'
            )

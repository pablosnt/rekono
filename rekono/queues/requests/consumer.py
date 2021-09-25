from executions.models import Request
from executions.exceptions import InvalidRequestException
from tools import executor as tools
from processes import executor as processes
from django_rq import job


@job('requests-queue')
def process_request(request: Request = None, parameters: list = []) -> None:
    if request:
        if request.tool:
            tools.execute(request, parameters)
        elif request.process:
            processes.execute(request, parameters)
        else:
            raise InvalidRequestException('Invalid request. Process or tool is required')

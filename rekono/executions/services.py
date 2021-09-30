import os
import signal

from django.utils import timezone
from executions.enums import Status
from executions.exceptions import InvalidRequestException
from executions.models import Execution
from queues.executions import utils


def cancel_request(request):
    if request.status in [Status.REQUESTED, Status.RUNNING]:
        executions = Execution.objects.filter(
            request=request,
            status__in=[Status.REQUESTED, Status.RUNNING]
        ).all()
        for execution in executions:
            if execution.rq_job_id:
                utils.cancel_job(execution.rq_job_id)
            if execution.rq_job_pid:
                os.kill(execution.rq_job_pid, signal.SIGKILL)
            execution.status = Status.CANCELLED
            execution.end = timezone.now()
            execution.save()
        request.status = Status.CANCELLED
        request.end = timezone.now()
        request.save()
    else:
        raise InvalidRequestException(f'Request {request.id} can not be cancelled')

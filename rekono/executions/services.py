import os
import signal

from django.utils import timezone
from executions.enums import Status
from executions.exceptions import InvalidTaskException
from executions.models import Execution
from queues.executions import utils


def cancel_task(task):
    if task.status in [Status.REQUESTED, Status.RUNNING]:
        executions = Execution.objects.filter(
            task=task,
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
        task.status = Status.CANCELLED
        task.end = timezone.now()
        task.save()
    else:
        raise InvalidTaskException(f'Task {task.id} can not be cancelled')

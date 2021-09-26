from django.db import connection
import django_rq


def cancel_execution(job_id):
    executions_queue = django_rq.get_queue('executions-queue')
    execution = executions_queue.fetch_job(job_id)
    execution.cancel()

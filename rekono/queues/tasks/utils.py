import django_rq
from rq.job import Job


def cancel_and_delete_job(job_id: str) -> Job:
    tasks_queue = django_rq.get_queue('tasks-queue')
    task = tasks_queue.fetch_job(job_id)
    if task:
        task.cancel()
        task.delete()
    return task

import logging

import django_rq
from rq.job import Job

logger = logging.getLogger()                                                    # Rekono logger


def cancel_job(queue_name: str, job_id: str) -> Job:
    '''Cancel a job based on his Id.

    Args:
        job_id (str): Job Id to be cancelled

    Returns:
        Job: Cancelled job
    '''
    queue = django_rq.get_queue(queue_name)                                     # Get queue by name
    job = queue.fetch_job(job_id)                                               # Get job to be cancelled by Id
    if job:
        logger.info(f'[Queues] Job {job_id} from {queue_name} has been cancelled')
        job.cancel()                                                            # Cancel job
    return job


def cancel_and_delete_job(queue_name: str, job_id: str) -> Job:
    '''Cancel and delete a job based on his Id.

    Args:
        job_id (str): Job Id to be cancelled and deleted

    Returns:
        Job: Cancelled and deleted job
    '''
    job = cancel_job(queue_name, job_id)                                        # Cancel job
    if job:
        logger.info(f'[Queues] Job {job_id} from {queue_name} has been deleted')
        job.delete()                                                            # Delete job
    return job

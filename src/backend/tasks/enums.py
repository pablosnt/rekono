from django.db import models

# Create your enums here.


class Status(models.TextChoices):
    '''Tasks statuses.'''

    REQUESTED = 'Requested'                                                     # Task execution doesn't start yet
    # Task execution has been skipped due to insufficient parameters
    SKIPPED = 'Skipped'
    RUNNING = 'Running'                                                         # Task execution is running right now
    # Task execution has been cancelled by the user
    CANCELLED = 'Cancelled'
    ERROR = 'Error'                                                             # Task execution finishes with errors
    COMPLETED = 'Completed'                                                     # Task execution finishes successfully


class TimeUnit(models.TextChoices):
    '''Time units supported for Task scheduling and repeating configuration.'''

    MINUTES = 'Minutes'
    HOURS = 'Hours'
    DAYS = 'Days'
    WEEKS = 'Weeks'

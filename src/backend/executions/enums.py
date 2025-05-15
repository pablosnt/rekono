# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db import models

# Create your enums here.


class Status(models.TextChoices):
    REQUESTED = "Requested"
    SKIPPED = "Skipped"
    RUNNING = "Running"
    CANCELLED = "Cancelled"
    ERROR = "Error"
    COMPLETED = "Completed"

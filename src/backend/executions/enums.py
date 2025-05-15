from django.db import models
from django.db.models.enums import Choices

# Create your enums here.


class Status(models.TextChoices):
    REQUESTED = "Requested"
    SKIPPED = "Skipped"
    RUNNING = "Running"
    CANCELLED = "Cancelled"
    ERROR = "Error"
    COMPLETED = "Completed"


Status: type[Choices] = Status  # https://github.com/google/pytype/issues/1048

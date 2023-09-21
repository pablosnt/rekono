from django.db import models

# Create your enums here.


class Status(models.TextChoices):
    REQUESTED = "Requested"
    SKIPPED = "Skipped"
    RUNNING = "Running"
    CANCELLED = "Cancelled"
    ERROR = "Error"
    COMPLETED = "Completed"

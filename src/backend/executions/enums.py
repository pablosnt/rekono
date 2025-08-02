"""Execution status enumerations for Rekono.

Defines available execution statuses for tracking progress of security
tool executions throughout their lifecycle.
"""

from django.db import models
from django.db.models.enums import Choices


class Status(models.TextChoices):
    """Enumeration of execution status values.

    Defines the different states an execution progresses through during
    its lifecycle from creation to completion.

    Attributes:
        REQUESTED (str): Execution requested but not yet queued
        SKIPPED (str): Execution skipped due to dependencies or conditions
        RUNNING (str): Execution currently being processed
        CANCELLED (str): Execution cancelled before completion
        ERROR (str): Execution failed with an error
        COMPLETED (str): Execution completed successfully
    """

    REQUESTED = "Requested"
    SKIPPED = "Skipped"
    RUNNING = "Running"
    CANCELLED = "Cancelled"
    ERROR = "Error"
    COMPLETED = "Completed"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
Status: type[Choices] = Status

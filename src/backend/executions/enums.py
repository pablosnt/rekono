"""Execution status enumerations for Rekono.

This module defines the available execution statuses that can be used
for tracking the progress of security tool executions in the system.
"""

from django.db import models
from django.db.models.enums import Choices


class Status(models.TextChoices):
    """Enumeration of execution status values.

    This class defines the different states that an execution can be in
    during its lifecycle from creation to completion.

    Attributes:
        REQUESTED (str): Execution has been requested but not yet queued.
        SKIPPED (str): Execution was skipped due to dependencies or conditions.
        RUNNING (str): Execution is currently being processed.
        CANCELLED (str): Execution was cancelled before completion.
        ERROR (str): Execution failed with an error.
        COMPLETED (str): Execution completed successfully.
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

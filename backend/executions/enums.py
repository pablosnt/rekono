"""Statuses that an execution goes through."""

from django.db import models
from django.db.models.enums import Choices


class Status(models.TextChoices):
    """Status of an execution, which also decides the status of its task.

    Attributes:
        REQUESTED: The execution is waiting in the queue.
        SKIPPED: The execution never ran, because the tool isn't installed, its
          arguments can't be built, or the task was rejected before starting.
        RUNNING: The tool is being executed.
        CANCELLED: The execution was cancelled before finishing.
        ERROR: The tool failed.
        COMPLETED: The tool finished and its output was parsed.
    """

    REQUESTED = "Requested"
    SKIPPED = "Skipped"
    RUNNING = "Running"
    CANCELLED = "Cancelled"
    ERROR = "Error"
    COMPLETED = "Completed"

    @classmethod
    def in_progress(cls) -> list[str]:
        """Return the statuses of the executions that didn't finish yet."""
        return [cls.REQUESTED, cls.RUNNING]

    @classmethod
    def finished(cls) -> list[str]:
        """Return the statuses of the executions that already finished."""
        return [cls.COMPLETED, cls.ERROR, cls.SKIPPED, cls.CANCELLED]


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Status: type[Choices] = Status

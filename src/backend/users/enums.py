from django.db import models
from django.db.models.enums import Choices


class Notification(models.TextChoices):
    """Notification choices for users."""

    DISABLED = "Disabled"  # All notifications disabled
    # Only notifications with executions made by the user
    MY_EXECUTIONS = "Only my executions"
    # Notifications with all executions made in user projects
    ALL_EXECUTIONS = "All executions"


Notification: type[Choices] = Notification  # https://github.com/google/pytype/issues/1048

from django.db import models
from django.db.models.enums import Choices


class Notification(models.TextChoices):
    # All notifications disabled except the security ones
    DISABLED = "Disabled"
    # Only notifications with executions started by the user
    MY_EXECUTIONS = "Only my executions"
    # Notifications with all executions from the projects that the user has access to
    ALL_EXECUTIONS = "All executions"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
Notification: type[Choices] = Notification

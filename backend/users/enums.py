"""Enumeration classes for user notification preferences.

Defines notification scope options for user preference management
with Django TextChoices implementation.
"""

from django.db import models
from django.db.models.enums import Choices


class Notification(models.TextChoices):
    """Notification scope preferences for user accounts.

    Defines the scope of notifications users receive about security executions.
    Controls which execution events trigger notifications to the user.

    Attributes:
        ONLY_ALERTS (str): Only alert notifications, execution notifications disabled
        MY_EXECUTIONS (str): Only notifications for executions started by the user
        ALL_EXECUTIONS (str): Notifications for all executions in accessible projects
    """

    ONLY_ALERTS = "Only alerts"
    MY_EXECUTIONS = "Only my executions"
    ALL_EXECUTIONS = "All executions"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Notification: type[Choices] = Notification

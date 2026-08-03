"""Enumeration classes for user notification preferences and OTP scopes.

Defines notification scope options for user preference management and the
purposes that a one-time password can be issued for, with Django TextChoices
implementation.
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


class OtpScope(models.IntegerChoices):
    """Purposes that a one-time password can be issued for.

    One-time passwords are bound to the operation they were created for, so an
    OTP sent for one workflow can't be replayed against another one. For
    example, an OTP sent to verify a new email address can't be used to reset
    the account password or to pass the MFA second factor.

    Attributes:
        INVITATION (str): Account creation after an invitation
        PASSWORD_RESET (str): Password reset, including the account enabling email
        EMAIL_VERIFICATION (str): Confirmation of a pending email address change
        MFA (str): Multi-factor authentication second factor sent via email
    """

    INVITATION = 1
    PASSWORD_RESET = 2
    EMAIL_VERIFICATION = 3
    MFA = 4


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Notification: type[Choices] = Notification
OtpScope: type[Choices] = OtpScope

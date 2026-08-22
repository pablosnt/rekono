"""Notification preferences of the users and purposes of their one-time passwords."""

from django.db import models
from django.db.models.enums import Choices


class Notification(models.TextChoices):
    """Executions that a user wants to be notified about.

    Attributes:
        ONLY_ALERTS: No execution notifications at all, only the triggered alerts.
        MY_EXECUTIONS: Only the executions of the tasks that the user started.
        ALL_EXECUTIONS: All the executions of the projects where the user is member.
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
        INVITATION: Account creation after an invitation.
        PASSWORD_RESET: Password reset, including the account enabling email.
        EMAIL_VERIFICATION: Confirmation of a pending email address change.
        MFA: Multi-factor authentication second factor sent via email.
    """

    INVITATION = 1
    PASSWORD_RESET = 2
    EMAIL_VERIFICATION = 3
    MFA = 4


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Notification: type[Choices] = Notification
OtpScope: type[Choices] = OtpScope

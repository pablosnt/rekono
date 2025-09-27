"""Django models for target denylist management.

Provides the TargetDenylist model for managing excluded targets in security
testing operations. The model ensures that sensitive or unauthorized targets
are prevented from being processed by security assessment tools.
"""

from django.db import models

from framework.models import BaseModel
from security.validators.input_validator import Regex, Validator


class TargetDenylist(BaseModel):
    """Model representing targets that should be excluded from security testing.

    Manages a centralized denylist of targets (IPs, domains, URLs) that must be
    excluded from all security assessment activities. Supports both administrative
    default entries and user-defined custom exclusions with proper validation.

    Attributes:
        target (TextField): The target pattern to exclude (max 100 characters)
        default (BooleanField): Whether this is a default system entry (read-only)

    Example:
        Create a custom denylist entry:

        ```python
        denylist = TargetDenylist.objects.create(
            target="192.168.1.0/24",
            default=False
        )
        ```
    """

    target = models.TextField(unique=True, max_length=100, validators=[Validator(Regex.TARGET_REGEX)])
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return string representation of the denylist entry.

        Returns:
            str: The target pattern being denied.
        """
        return self.target

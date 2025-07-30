"""HTTP header models for Rekono.

This module defines the HttpHeader model which stores custom HTTP headers
used in security testing and penetration testing workflows. The model
supports both target-specific and user-specific headers with validation
and parsing capabilities for integration with security testing tools.
"""

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class HttpHeader(BaseInput):
    """HTTP header model for storing custom request headers.

    This model represents custom HTTP headers that can be used in security
    testing and penetration testing workflows. Headers can be associated
    with specific targets or users, enabling customized request headers
    for different testing scenarios.

    Attributes:
        target (ForeignKey): The target this header is associated with.
            Optional field for target-specific headers.
        user (ForeignKey): The user this header is associated with.
            Optional field for user-specific headers.
        key (TextField): The HTTP header name/key with validation.
        value (TextField): The HTTP header value with validation.
    """

    target = models.ForeignKey(
        Target,
        related_name="http_headers",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="http_headers",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    key = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="key", deny_injections=True)],
    )
    value = models.TextField(
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="value", deny_injections=True)],
    )

    _filters = [BaseInput.Filter(type=str, field="key")]
    _parse_mapping = {InputKeyword.HEADERS: lambda instance: {instance.key: instance.value}}
    _project_field = "target__project"

    class Meta:
        """Meta configuration with database constraints.

        This class defines unique constraints to ensure data integrity:
        - Global headers (no target, no user) must have unique keys
        - User-specific headers must have unique user+key combinations
        - Target-specific headers must have unique target+key combinations
        """

        constraints = [
            # Global headers: unique key when both target and user are null
            models.UniqueConstraint(
                "key",
                name="unique_http_headers",
                condition=models.Q(user__isnull=True, target__isnull=True),
            ),
            # User-specific headers: unique user+key when target is null
            models.UniqueConstraint(
                "user",
                "key",
                name="unique_http_headers_2",
                condition=models.Q(target__isnull=True),
            ),
            # Target-specific headers: unique target+key when user is null
            models.UniqueConstraint(
                "target",
                "key",
                name="unique_http_headers_3",
                condition=models.Q(user__isnull=True),
            ),
        ]

    def __str__(self) -> str:
        """String representation of the HTTP header record.

        Returns:
            str: String in format "parent - key" where parent is target or user,
                or just "key" if no parent is associated.
        """
        parent = self.target or self.user
        return f"{parent.__str__()} - {self.key}" if parent else self.key

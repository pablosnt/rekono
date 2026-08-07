"""Model of the HTTP headers that the tools send."""

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class HttpHeader(BaseInput):
    """Header that the tools include in the requests that they send.

    The scope of a header is decided by the relations that it has: a header with a
    target applies to everything scanned in that target, a header with a user
    applies to everything that the user scans, and a header with neither of them
    applies to all the executions.

    Attributes:
        target: Target that the header applies to.
        user: User that the header applies to.
        key: Name of the header.
        value: Value of the header.
    """

    target = models.ForeignKey(Target, related_name="http_headers", on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL, related_name="http_headers", on_delete=models.CASCADE, blank=True, null=True
    )
    key = models.TextField(max_length=100, validators=[Validator(Regex.NAME, code="key", deny_injections=True)])
    value = models.TextField(max_length=500, validators=[Validator(Regex.TEXT, code="value", deny_injections=True)])

    _filters = [BaseInput.Filter(type=str, field="key")]
    _parse_mapping = {InputKeyword.HEADERS: lambda instance, task: {instance.key: instance.value}}
    _project_field = "target__project"

    class Meta:
        """Model configuration, making the header key unique within each scope."""

        constraints = [
            models.UniqueConstraint(
                "key",
                name="unique_http_headers",
                condition=models.Q(user__isnull=True, target__isnull=True),
            ),
            models.UniqueConstraint(
                "user",
                "key",
                name="unique_http_headers_2",
                condition=models.Q(target__isnull=True),
            ),
            models.UniqueConstraint(
                "target",
                "key",
                name="unique_http_headers_3",
                condition=models.Q(user__isnull=True),
            ),
        ]

    def __str__(self) -> str:
        """Return the header key, with the target or the user that it applies to."""
        parent = self.target or self.user
        return f"{parent.__str__()} - {self.key}" if parent else self.key

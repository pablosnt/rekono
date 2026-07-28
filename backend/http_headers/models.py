"""HTTP Header models for security testing configuration management.

Provides persistent storage and validation for HTTP headers used in security
testing workflows. Supports multi-scope configurations including global,
user-specific, and target-specific header management with comprehensive
validation and constraint enforcement.
"""

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class HttpHeader(BaseInput):
    """HTTP header configuration model for security testing operations.

    Provides persistent storage for HTTP headers used during web application
    security testing and reconnaissance activities. Supports three distinct
    scopes: global headers applied to all operations, user-specific headers
    for individual security professionals, and target-specific headers for
    specialized testing scenarios.

    The model inherits from BaseInput to integrate seamlessly with the Rekono
    execution framework, enabling automatic header injection during security
    scans and manual testing operations. All header data is validated to
    prevent injection attacks and ensure security compliance.

    Attributes:
        target (ForeignKey): Target this header applies to (optional, deleted
                            along with the target)
        user (ForeignKey): User this header applies to (optional, deleted
                          along with the user)
        key (TextField): HTTP header name (required, max 100 chars, validated
                        against Regex.NAME with injection checks)
        value (TextField): HTTP header value (required, max 500 chars,
                          validated against Regex.TEXT with injection checks)
        _filters (list): Filter configuration allowing headers to be filtered by key
        _parse_mapping (dict): Maps InputKeyword.HEADERS to a dict pairing this
                              header's key and value
        _project_field (str): Path to the project via the target relation, used
                             for project-level access control

    Constraints:
        - Global headers: Unique key when both target and user are null
        - User-specific: Unique user+key combination when target is null
        - Target-specific: Unique target+key combination when user is null

    Example:
        ```python
        # Global authentication header
        global_header = HttpHeader.objects.create(
            key="Authorization",
            value="Bearer global-token"
        )

        # User-specific header
        user_header = HttpHeader.objects.create(
            key="X-User-Token",
            value="user-specific-token",
            user=user_instance
        )

        # Target-specific header
        target_header = HttpHeader.objects.create(
            key="X-Target-Auth",
            value="target-specific-token",
            target=target_instance
        )
        ```
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
        """Meta configuration for HttpHeader model.

        Defines database constraints ensuring header uniqueness within each
        scope (global, user-specific, target-specific) to prevent conflicting
        configurations during security testing operations.

        Constraints:
            unique_http_headers: Global headers have unique keys
            unique_http_headers_2: User-specific headers have unique user+key
            unique_http_headers_3: Target-specific headers have unique target+key
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
        """Return string representation of the HTTP header.

        Provides a human-readable representation showing the header scope
        and key name for easy identification in admin interfaces and logs.

        Returns:
            str: Formatted string showing parent context and header key,
                 or just the key for global headers.
        """
        parent = self.target or self.user
        return f"{parent.__str__()} - {self.key}" if parent else self.key

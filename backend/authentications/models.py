"""Authentication models for Rekono.

Defines the Authentication model for storing encrypted authentication credentials.
Supports multiple authentication types with validation, encryption, and parsing
capabilities for security testing tool integration.
"""

import base64

from django.db import models

from authentications.enums import AuthenticationType
from framework.enums import InputKeyword
from framework.models import BaseEncrypted, BaseInput
from security.validators.input_validator import Regex, Validator
from target_ports.models import TargetPort


class Authentication(BaseInput, BaseEncrypted):
    """Authentication model for storing encrypted credentials.

    Represents authentication credentials for security testing with support for
    multiple authentication types, automatic encryption, and validation.

    Security Features:
        - Automatic encryption for sensitive credential data
        - Input validation with injection prevention
        - Project-scoped access control
        - Integration with security testing tools

    Attributes:
        name (TextField): Username/name for authentication (optional, max 100 chars)
        _secret (TextField): Encrypted password/token (stored as 'secret', max 500 chars)
        type (TextField): Authentication type from AuthenticationType enum
        target_port (OneToOneField): Associated target port (one-to-one relationship)

    Example:
        Create basic authentication:

        ```python
        auth = Authentication.objects.create(
            name="admin",
            secret="password123",
            type=AuthenticationType.BASIC,
            target_port=target_port
        )
        ```
    """

    name = models.TextField(
        max_length=100, validators=[Validator(Regex.NAME, code="name", deny_injections=True)], null=True, blank=True
    )
    _secret = models.TextField(
        max_length=500,
        validators=[Validator(Regex.SECRET, code="secret", deny_injections=True)],
        null=True,
        blank=True,
        db_column="secret",
    )
    type = models.TextField(max_length=8, choices=AuthenticationType.choices)
    target_port = models.OneToOneField(
        TargetPort,
        related_name="authentication",
        on_delete=models.CASCADE,
    )

    # Filter configuration for BaseInput
    _filters = [BaseInput.Filter(type=AuthenticationType, field="type")]
    # Parse mapping for integration with hacking tools
    _parse_mapping = {
        InputKeyword.COOKIE_NAME: lambda instance, task: (
            instance.name if instance.type == AuthenticationType.COOKIE else None
        ),
        InputKeyword.SECRET: "secret",
        InputKeyword.CREDENTIAL_TYPE: "type",
        InputKeyword.CREDENTIAL_TYPE_LOWER: lambda instance, task: instance.type.lower(),
        InputKeyword.TOKEN: "token",
        InputKeyword.USERNAME: lambda instance, task: (
            instance.name if instance.type == AuthenticationType.BASIC else None
        ),
    }
    # Encryption and project field configuration
    _encrypted_field = "_secret"
    _project_field = "target_port__target__project"

    @property
    def token(self) -> str:
        """Generate authentication token based on type.

        For Basic auth, returns base64 encoded username:password.
        For other types, returns the secret directly.

        Returns:
            str: Formatted authentication token
        """
        return (
            base64.b64encode(f"{self.name}:{self.secret}".encode()).decode()
            if self.type == AuthenticationType.BASIC
            else self.secret
        )

    def __str__(self) -> str:
        """String representation of the authentication record.

        Returns:
            str: String in format "target_port - name" or just "name"
        """
        return f"{self.target_port.__str__()} - {self.name}" if self.target_port else self.name

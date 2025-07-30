"""Authentication models for Rekono.

This module defines the Authentication model which stores encrypted authentication
credentials for various authentication types (Basic, Bearer, Cookie, Digest,
JWT, NTLM, Token). The model includes validation, encryption, and parsing
capabilities for integration with security testing tools.
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

    This model represents authentication credentials used for security testing
    and penetration testing. It supports multiple authentication types and
    provides encryption for sensitive data, validation for input fields, and
    parsing capabilities for integration with testing tools.

    Attributes:
        name (TextField): The name/username for the authentication credential.
            Optional field with validation for name format and injection prevention.
        _secret (TextField): The encrypted secret/password/token for authentication.
            Stored in database as 'secret' column with validation and encryption.
        type (TextField): The type of authentication (Basic, Bearer, Cookie, etc.).
            Choices defined by AuthenticationType enum.
        target_port (OneToOneField): The target port this authentication is
            associated with. One-to-one relationship with TargetPort model.
    """

    name = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name", deny_injections=True)],
        null=True,
        blank=True,
    )
    _secret = models.TextField(
        max_length=500,
        validators=[Validator(Regex.SECRET.value, code="secret", deny_injections=True)],
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
    # Parse mapping for integration with hackign tools
    _parse_mapping = {
        InputKeyword.COOKIE_NAME: lambda instance: (
            instance.name if instance.type == AuthenticationType.COOKIE else None
        ),
        InputKeyword.SECRET: "secret",
        InputKeyword.CREDENTIAL_TYPE: "type",
        InputKeyword.CREDENTIAL_TYPE_LOWER: lambda instance: instance.type.lower(),
        InputKeyword.TOKEN: "token",
        InputKeyword.USERNAME: lambda instance: (instance.name if instance.type == AuthenticationType.BASIC else None),
    }
    # Encryption and project field configuration
    _encrypted_field = "_secret"
    _project_field = "target_port__target__project"

    @property
    def token(self) -> str:
        """Generate authentication token based on type.

        For Basic authentication, returns base64 encoded username:password.
        For other types, returns the secret directly.

        Returns:
            str: The authentication token formatted according to the type.
        """
        return (
            base64.b64encode(f"{self.name}:{self.secret}".encode()).decode()
            if self.type == AuthenticationType.BASIC
            else self.secret
        )

    def __str__(self) -> str:
        """String representation of the authentication record.

        Returns:
            str: String in format "target_port - name" or just "name" if no
                target port is associated.
        """
        return (f"{self.target_port.__str__()} - " if self.target_port else "") + self.name

"""Model of the credentials used to authenticate against the target services."""

import base64

from django.db import models

from authentications.enums import AuthenticationType
from framework.enums import InputKeyword
from framework.models import BaseEncrypted, BaseInput
from security.validators.input_validator import Regex, Validator
from target_ports.models import TargetPort


class Authentication(BaseInput, BaseEncrypted):
    """Credential that the tools can use to authenticate against a target port.

    It's also an input of the executions, so the tools receive the credential in
    the format that their arguments expect.

    Attributes:
        name: Username, or cookie name for the cookie credentials.
        type: Way in which the credential is sent to the service.
        target_port: Port whose service accepts this credential.
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

    _filters = [BaseInput.Filter(type=AuthenticationType, field="type")]
    _parse_mapping = {
        InputKeyword.COOKIE_NAME: lambda instance, task: (
            instance.name if instance.type == AuthenticationType.COOKIE else None
        ),
        InputKeyword.SECRET: "secret",
        InputKeyword.CREDENTIAL_TYPE: "type",
        InputKeyword.CREDENTIAL_TYPE_LOWER: lambda instance, task: instance.type.lower(),
        InputKeyword.TOKEN: "token",
        InputKeyword.USERNAME: lambda instance, task: (
            instance.name
            if instance.type in [AuthenticationType.BASIC, AuthenticationType.DIGEST, AuthenticationType.NTLM]
            else None
        ),
    }
    _encrypted_field = "_secret"
    _project_field = "target_port__target__project"

    @property
    def token(self) -> str:
        """The credential value as the tools need to send it.

        Basic credentials are encoded as the base64 of "username:password", which is
        what the Authorization header expects, and the rest are sent as they are.
        """
        return (
            base64.b64encode(f"{self.name}:{self.secret}".encode()).decode()
            if self.type == AuthenticationType.BASIC
            else self.secret
        )

    def __str__(self) -> str:
        """Return the target port and the name of the credential."""
        return f"{self.target_port.__str__()} - {self.name}" if self.target_port else self.name

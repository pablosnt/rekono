import base64

from django.db import models

from authentications.enums import AuthenticationType
from framework.enums import InputKeyword
from framework.models import BaseEncrypted, BaseInput
from security.validators.input_validator import Regex, Validator
from target_ports.models import TargetPort

# Create your models here.


class Authentication(BaseInput, BaseEncrypted):
    """Authentication model."""

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

    filters = [BaseInput.Filter(type=AuthenticationType, field="type")]
    parse_mapping = {
        InputKeyword.COOKIE_NAME: lambda instance: (
            instance.name if instance.type == AuthenticationType.COOKIE else None
        ),
        InputKeyword.SECRET: "secret",
        InputKeyword.CREDENTIAL_TYPE: "type",
        InputKeyword.CREDENTIAL_TYPE_LOWER: lambda instance: instance.type.lower(),
        InputKeyword.TOKEN: lambda instance: instance.get_token(),
        InputKeyword.USERNAME: lambda instance: (instance.name if instance.type == AuthenticationType.BASIC else None),
    }
    _encrypted_field = "_secret"
    project_field = "target_port__target__project"

    def get_token(self) -> str:
        return (
            base64.b64encode(f"{self.name}:{self.secret}".encode()).decode()
            if self.type == AuthenticationType.BASIC
            else self.secret
        )

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return (f"{self.target_port.__str__()} - " if self.target_port else "") + self.name

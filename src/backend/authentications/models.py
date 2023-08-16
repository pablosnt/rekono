import base64
from typing import Any, Dict

from authentications.enums import AuthenticationType
from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput
from projects.models import Project
from security.input_validation import Regex, Validator
from target_ports.models import TargetPort

# Create your models here.


class Authentication(BaseInput):
    """Authentication model."""

    target_port = models.OneToOneField(
        TargetPort, related_name="authentication", on_delete=models.CASCADE
    )
    name = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    secret = models.TextField(
        max_length=500,
        validators=[Validator(Regex.SECRET.value, code="secret")],
    )
    type = models.TextField(max_length=8, choices=AuthenticationType.choices)

    filters = [BaseInput.Filter(type=AuthenticationType, field="type")]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = self.target_port.parse()
        output.update(
            {
                InputKeyword.COOKIE_NAME.name.lower(): self.name
                if self.type == AuthenticationType.COOKIE
                else None,
                InputKeyword.SECRET.name.lower(): self.secret,
                InputKeyword.CREDENTIAL_TYPE.name.lower(): self.type,
                InputKeyword.CREDENTIAL_TYPE_LOWER.name.lower(): self.type.lower(),
            }
        )
        if self.type == AuthenticationType.BASIC:
            output.update(
                {
                    InputKeyword.USERNAME.name.lower(): self.name,
                    InputKeyword.TOKEN.name.lower(): base64.b64encode(
                        f"{self.name}:{self.credential}".encode()
                    ).decode(),
                }
            )
        else:
            output.update(
                {
                    InputKeyword.USERNAME.name.lower(): None,
                    InputKeyword.TOKEN.name.lower(): self.secret,
                }
            )
        return output

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target_port.__str__()} - {self.name}"

    def get_project(self) -> Project:
        """Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        """
        return self.target_port.target.project

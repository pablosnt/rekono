from typing import Any

from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput
from parameters.framework.models import InputParameter
from security.validators.input_validator import Regex, Validator

# Create your models here.


class InputTechnology(InputParameter):
    """Input technology model."""

    name = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name", deny_injections=True)],
    )
    version = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="version", deny_injections=True)],
        blank=True,
        null=True,
    )

    filters = [BaseInput.Filter(type=str, field="name", contains=True)]

    # TODO: Move to just a mapping?
    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        return {
            InputKeyword.TECHNOLOGY.name.lower(): self.name,
            InputKeyword.VERSION.name.lower(): self.version or "",
        }

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.name} - {self.version}" if self.version else self.name


class InputVulnerability(InputParameter):
    """Input vulnerability model."""

    cve = models.TextField(
        max_length=20,
        validators=[Validator(Regex.CVE.value, code="cve", deny_injections=True)],
    )

    filters = [
        BaseInput.Filter(type=str, field="cve", processor=lambda v: "cve"),
        BaseInput.Filter(type=str, field="cve", processor=lambda v: v.lower()),
    ]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        return {InputKeyword.CVE.name.lower(): self.cve}

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.cve

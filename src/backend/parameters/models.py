from typing import Any, Dict

from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput
from security.input_validator import Regex, Validator
from targets.models import Target

# Create your models here.


class InputTechnology(BaseInput):
    """Input technology model."""

    target = models.ForeignKey(
        Target, related_name="input_technologies", on_delete=models.CASCADE
    )
    name = models.TextField(
        max_length=100, validators=[Validator(Regex.NAME.value, code="name")]
    )
    version = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="version")],
        blank=True,
        null=True,
    )

    filters = [BaseInput.Filter(type=str, field="name", contains=True)]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["target", "name", "version"], name="unique_input_technology"
            )
        ]

    def parse(
        self, target: Target = None, accumulated: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = self.target.parse(target, accumulated)
        output[InputKeyword.TECHNOLOGY.name.lower()] = self.name
        if self.version:
            output[InputKeyword.VERSION.name.lower()] = self.version
        return output

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target.__str__()} - {self.name}{f' - {self.version}' if self.version else ''}"

    @classmethod
    def get_project_field(cls) -> str:
        return "target__project"


class InputVulnerability(BaseInput):
    """Input vulnerability model."""

    target = models.ForeignKey(
        Target, related_name="input_vulnerabilities", on_delete=models.CASCADE
    )
    cve = models.TextField(
        max_length=20, validators=[Validator(Regex.CVE.value, code="cve")]
    )

    filters = [
        BaseInput.Filter(type=str, field="cve", processor=lambda v: "cve"),
        BaseInput.Filter(type=str, field="cve", processor=lambda v: v.lower()),
    ]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["target", "cve"], name="unique_input_vulnerability"
            )
        ]

    def parse(
        self, target: Target = None, accumulated: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = self.target.parse(target, accumulated)
        output[InputKeyword.CVE.name.lower()] = self.cve
        return output

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target.__str__()} - {self.cve}"

    @classmethod
    def get_project_field(cls) -> str:
        return "target__project"

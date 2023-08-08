from typing import Any, Dict

from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput
from projects.models import Project
from security.input_validation import validate_number
from targets.models import Target

# Create your models here.


class TargetPort(BaseInput):
    """Target port model."""

    target = models.ForeignKey(
        Target, related_name="target_ports", on_delete=models.CASCADE
    )
    port = models.IntegerField(validators=[validate_number])

    filters = [BaseInput.Filter(type=int, field="port")]

    class Meta:
        unique_together = ["target", "port"]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = {
            InputKeyword.TARGET.name.lower(): self.target.target,
            InputKeyword.HOST.name.lower(): self.target.target,
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): [self.port],
            InputKeyword.URL.name.lower(): self._get_url(self.target.target, self.port),
        }
        if accumulated and InputKeyword.PORTS.name.lower() in accumulated:
            output[InputKeyword.PORTS.name.lower()] = accumulated[
                InputKeyword.PORTS.name.lower()
            ]
            output[InputKeyword.PORTS.name.lower()].append(self.port)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(port) for port in output[InputKeyword.PORTS.name.lower()]]
        )
        return output

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target.target} - {self.port}"

    def get_project(self) -> Project:
        """Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        """
        return self.target.project

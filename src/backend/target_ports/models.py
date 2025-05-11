from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from security.validators.input_validator import Regex, Validator
from targets.models import Target

# Create your models here.


class TargetPort(BaseInput):
    """Target port model."""

    target = models.ForeignKey(Target, related_name="target_ports", on_delete=models.CASCADE)
    port = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    path = models.TextField(
        max_length=100,
        validators=[Validator(Regex.PATH.value, code="path")],
        blank=True,
        null=True,
    )

    filters = [BaseInput.Filter(type=int, field="port")]
    project_field = "target__project"

    class Meta:
        constraints = [models.UniqueConstraint(fields=["target", "port"], name="unique_target_port")]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = self.authentication.parse(accumulated) if self.authentication else {}
        ports = (accumulated or {}).get(InputKeyword.PORTS.name.lower(), []) + [self.port]
        path = self._clean_path(self.path)
        return {
            **output,
            InputKeyword.TARGET.name.lower(): self.target.target,
            InputKeyword.HOST.name.lower(): self.target.target,
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): ports,
            InputKeyword.ENDPOINT.name.lower(): self._clean_path(path),
            InputKeyword.PORTS_COMMAS.name.lower(): ",".join([str(p) for p in ports]),
            InputKeyword.URL.name.lower(): self._get_url(self.target.target, self.port, path),
        }

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target.__str__()} - {self.port}"

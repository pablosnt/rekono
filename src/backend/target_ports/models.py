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
    parse_mapping = {
        InputKeyword.TARGET: lambda instance: instance.target.target,
        InputKeyword.HOST: lambda instance: instance.target.target,
        InputKeyword.PORT: "port",
        InputKeyword.PORTS: lambda instance: [instance.port],
        InputKeyword.ENDPOINT: lambda instance: instance._clean_path(instance.path),
        InputKeyword.URL: lambda instance: instance._get_url(
            instance.target.target, instance.port, instance._clean_path(path)
        ),
    }
    parse_dependencies = ["authentication"]
    project_field = "target__project"

    class Meta:
        constraints = [models.UniqueConstraint(fields=["target", "port"], name="unique_target_port")]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        output = super().parse(accumulated)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(p) for p in output.get(InputKeyword.PORTS_COMMAS.name.lower()) or []]
        )
        return output

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.target.__str__()} - {self.port}"

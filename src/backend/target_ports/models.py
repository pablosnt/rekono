from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class TargetPort(BaseInput):
    target = models.ForeignKey(Target, related_name="target_ports", on_delete=models.CASCADE)
    port = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    path = models.TextField(max_length=100, validators=[Validator(Regex.PATH, code="path")], blank=True, null=True)

    _filters = [BaseInput.Filter(type=int, field="port")]
    _parse_mapping = {
        InputKeyword.TARGET: lambda instance: instance.target.target,
        InputKeyword.HOST: lambda instance: instance.target.target,
        InputKeyword.PORT: "port",
        InputKeyword.PORTS: lambda instance: [instance.port],
        InputKeyword.ENDPOINT: lambda instance: instance.clean_path(instance.path),
        InputKeyword.URL: lambda instance: instance.get_url(
            instance.target.target, instance.port, instance.clean_path(instance.path)
        ),
    }
    _parse_dependencies = ["authentication"]
    _project_field = "target__project"

    class Meta:
        constraints = [models.UniqueConstraint(fields=["target", "port"], name="unique_target_port")]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        output = super().parse(accumulated)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(p) for p in output.get(InputKeyword.PORTS.name.lower()) or []]
        )
        return output

    def __str__(self) -> str:
        return f"{self.target.__str__()} - {self.port}"

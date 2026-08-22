"""Model of the ports of a target that the scans must focus on."""

from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class TargetPort(BaseInput):
    """Port of a target where a service that must be scanned is exposed.

    It's an input of the executions, so the tools that accept a port receive it
    together with the path and the credential of that service.

    Attributes:
        target: Target where the service is exposed.
        port: Port where the service is listening.
        path: Path where a web service is exposed, if it isn't the root one.
    """

    target = models.ForeignKey(Target, related_name="target_ports", on_delete=models.CASCADE)
    port = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    path = models.TextField(max_length=100, validators=[Validator(Regex.PATH, code="path")], blank=True, null=True)

    _filters = [BaseInput.Filter(type=int, field="port")]
    # "target" is left out of _parse_dependencies below so Target.parse() doesn't run its own
    # get_url() probe, which the port-scoped URL here would immediately overwrite
    _parse_mapping = {
        InputKeyword.TARGET: lambda instance, task: f"{instance.target.target}:{instance.port}",
        InputKeyword.HOST: lambda instance, task: instance.target.target,
        InputKeyword.PORT: "port",
        InputKeyword.PORTS: lambda instance, task: [instance.port],
        InputKeyword.ENDPOINT: lambda instance, task: instance.clean_path(instance.path),
        InputKeyword.URL: lambda instance, task: instance.get_url(
            instance.target.target, instance.port, instance.clean_path(instance.path), task=task
        ),
    }
    _parse_dependencies = ["authentication"]
    _project_field = "target__project"

    class Meta:
        """Model configuration, allowing each port to be defined once per target."""

        constraints = [models.UniqueConstraint(fields=["target", "port"], name="unique_target_port")]

    def parse(self, task: Any, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get the keywords of this target port, including the comma-separated ports.

        The keyword with the ports joined by commas is calculated here, and not in
        the parse mapping, because it must include the ports of the other target
        ports of the same execution.

        Args:
            task: Task of the execution, forwarded to the base implementation.
            accumulated: Keywords already provided by the other inputs of the same
              execution, whose ports are joined with the ones of this target port.

        Returns:
            The keywords of this target port, including the comma-separated ports.
        """
        output = super().parse(task, accumulated)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(p) for p in output.get(InputKeyword.PORTS.name.lower()) or []]
        )
        return output

    def __str__(self) -> str:
        """Return the target and the port."""
        return f"{self.target.__str__()} - {self.port}"

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create the port finding equivalent to this target port.

        Args:
            execution: Execution that the created finding belongs to.
            **fields: Extra values for the finding, unused because a target port
              only provides the port itself.

        Returns:
            The new port finding, related to the host finding of the target, or None
            if that host finding can't be created.
        """
        from findings.models import Port

        host = self.target.create_finding_from_user_input(execution)
        if host:
            return Port.objects.create_finding(
                execution, **{**fields, "host": host, "port": self.port, "created_from_user_input": True}
            )

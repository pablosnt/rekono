"""Target port models for Rekono.

Defines the TargetPort model for managing port-specific targeting within
security testing workflows. Provides input parsing capabilities for security
tool integration and supports authentication credential association.
"""

from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from findings.models import Port
from framework.enums import InputKeyword
from framework.models import BaseInput
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class TargetPort(BaseInput):
    """Model representing a target port for security testing operations.

    Represents a specific port on a target that can be subject to security testing.
    Extends BaseInput to provide parsing capabilities for integration with security
    testing tools and frameworks. Supports optional path specification for
    web-based services and authentication credential association.

    Attributes:
        target (ForeignKey): The target this port belongs to
        port (IntegerField): Port number with validation (0-65535)
        path (TextField): Optional path for web services (max 100 chars,
                          validated)

    Example:
        Create a target port for HTTP service:

        ```python
        target_port = TargetPort.objects.create(
            target=my_target,
            port=80,
            path="/api/v1"
        )
        ```
    """

    target = models.ForeignKey(Target, related_name="target_ports", on_delete=models.CASCADE)
    port = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(65535)])
    path = models.TextField(max_length=100, validators=[Validator(Regex.PATH, code="path")], blank=True, null=True)

    _filters = [BaseInput.Filter(type=int, field="port")]
    # _parse_dependencies is not used to avoid recalculation of URLs
    _parse_mapping = {
        InputKeyword.TARGET: lambda instance, target: f"{instance.target.target}:{instance.port}",
        InputKeyword.HOST: lambda instance, target: instance.target.target,
        InputKeyword.PORT: "port",
        InputKeyword.PORTS: lambda instance, target: [instance.port],
        InputKeyword.ENDPOINT: lambda instance, target: instance.clean_path(instance.path),
        InputKeyword.URL: lambda instance, target: instance.get_url(
            target, instance.target.target, instance.port, instance.clean_path(instance.path)
        ),
    }
    _parse_dependencies = ["authentication"]
    _project_field = "target__project"

    class Meta:
        """Meta configuration for the TargetPort model.

        Defines database constraints and table-level configuration for
        target port instances.

        Attributes:
            constraints (list): Database constraints including unique constraint
                              for target-port combinations
        """

        constraints = [models.UniqueConstraint(fields=["target", "port"], name="unique_target_port")]

    def parse(self, target: Any, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Parse target port data for security tool integration.

        Extends the base parsing functionality to include comma-separated ports
        format for tools that require specific port list formatting.

        Args:
            accumulated (dict): Accumulated parsing data from other inputs

        Returns:
            dict: Parsed data including port information in multiple formats
        """
        output = super().parse(target, accumulated)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(p) for p in output.get(InputKeyword.PORTS.name.lower()) or []]
        )
        return output

    def __str__(self) -> str:
        """String representation of the target port.

        Returns:
            str: String in format "target - port"
        """
        return f"{self.target.__str__()} - {self.port}"

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        host = self.target.create_finding_from_user_input(execution)
        if host:
            return Port.objects.create(
                Port, execution, **{**fields, "host": host, "port": self.port, "created_from_user_input": True}
            )

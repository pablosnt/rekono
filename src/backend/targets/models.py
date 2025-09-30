"""Target models for Rekono.

Defines the Target model for managing security testing targets with automatic
type detection, validation, and input parsing capabilities for security tool
integration.
"""

import ipaddress
import re
import socket
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from projects.models import Project
from security.validators.input_validator import Regex
from security.validators.target_validator import TargetValidator
from targets.enums import TargetType


class Target(BaseInput):
    """Model representing a security testing target.

    Represents a target for security testing operations with automatic type
    detection and validation. Supports multiple target formats including IP
    addresses, networks, IP ranges, and domain names. Extends BaseInput to
    provide parsing capabilities for integration with security testing tools.

    Attributes:
        project (ForeignKey): The project this target belongs to
        target (TextField): Target specification (IP, domain, network, etc.)
        type (TextField): Automatically detected target type from TargetType enum

    Example:
        Create a target for domain testing:

        ```python
        target = Target.objects.create(
            project=my_project,
            target="example.com",
            type=TargetType.DOMAIN
        )
        ```
    """

    project = models.ForeignKey(Project, related_name="targets", on_delete=models.CASCADE)
    target = models.TextField(max_length=100, validators=[TargetValidator(Regex.TARGET)])
    type = models.TextField(max_length=10, choices=TargetType.choices)

    _filters = [BaseInput.Filter(type=TargetType, field="type")]
    _parse_mapping = {
        InputKeyword.TARGET: "target",
        InputKeyword.HOST: "target",
        InputKeyword.URL: lambda instance, target: instance.get_url(target, instance.target),
    }
    _project_field = "project"

    class Meta:
        """Meta configuration for the Target model.

        Defines database constraints and table-level configuration for
        target instances.

        Attributes:
            constraints (list): Database constraints including unique constraint
                              for project-target combinations
        """

        constraints = [models.UniqueConstraint(fields=["project", "target"], name="unique_target")]

    @staticmethod
    def get_type(target: str) -> str:
        """Automatically detect and classify the target type.

        Analyzes the target specification to determine its type and performs
        validation to ensure the target is valid and reachable. Supports
        multiple target formats with intelligent classification.

        Target Type Detection Logic:
            1. IPv4/IPv6 address detection with private vs public classification
            2. CIDR network notation validation and detection
            3. IP range pattern matching (hyphen-separated)
            4. Domain name resolution validation

        Args:
            target (str): Target specification to classify

        Returns:
            str: Target type from TargetType enum

        Raises:
            ValidationError: If target format is invalid or unsupported
        """
        try:
            # Check if target is an IP address (IPv4 or IPv6)
            ip = ipaddress.ip_address(target)
            if ip.is_private:  # Private IP (also for IPv6)
                return TargetType.PRIVATE_IP
            else:  # Public IP (also for IPv4)
                return TargetType.PUBLIC_IP
        except ValueError:
            pass  # Target is not an IP address
        try:
            ipaddress.ip_network(target)  # Check if target is a network
            return TargetType.NETWORK
        except ValueError:
            pass  # Target is not a network
        # Check if target is an IP range
        if bool(re.fullmatch(Regex.IP_RANGE.value, target)):
            return TargetType.IP_RANGE
        try:
            socket.gethostbyname(target)  # Check if target is a Domain
            return TargetType.DOMAIN
        except socket.gaierror:
            pass
        BaseInput.logger.warning(f"[Security] Invalid target {target}")
        # Target is invalid or target type is not supported
        raise ValidationError(
            "Invalid target. IP address, IP range or domain is required",
            code="target",
            params={"value": target},
        )

    def __str__(self) -> str:
        """String representation of the target.

        Returns:
            str: Target specification string
        """
        return self.target

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        from findings.models import Host

        if self.type == TargetType.DOMAIN:
            fields["ip"] = socket.gethostbyname(self.target.target)
            fields["domain"] = self.target
        elif self.type in [TargetType.PRIVATE_IP, TargetType.PUBLIC_IP]:
            fields["ip"] = self.target
        else:
            return None
        return Host.objects.create_finding(Host, execution, **{**fields, "created_from_user_input": True})

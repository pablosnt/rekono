import ipaddress
import logging
import re
import socket
from typing import Any, Dict

from django.core.exceptions import ValidationError
from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput
from projects.models import Project
from security.input_validation import IP_RANGE_REGEX
from targets.enums import TargetType

# Create your models here.

logger = logging.getLogger()  # Rekono logger


class Target(BaseInput):
    project = models.ForeignKey(
        Project, related_name="targets", on_delete=models.CASCADE
    )
    target = models.TextField(max_length=100)  # Target IP, domain or network
    type = models.TextField(max_length=10, choices=TargetType.choices)  # Target type

    filters = [BaseInput.Filter(type=TargetType, field="type")]

    class Meta:
        unique_together = ["project", "target"]

    @staticmethod
    def get_type(target: str) -> str:
        """Get target type from target address.

        Args:
            target (str): Target value

        Raises:
            ValidationError: Raised if target doesn't match any supported type

        Returns:
            str: Target type associated to the target
        """
        if target in [
            "127.0.0.1",
            "localhost",
            "frontend",
            "backend",
            "postgres",
            "redis",
            "initialize",
            "tasks-worker",
            "executions-worker",
            "findings-worker",
            "emails-worker",
            "telegram-bot",
            "nginx",
        ]:
            # Target is invalid
            raise ValidationError({"target": f"Invalid target {target}"})
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
        if bool(re.fullmatch(IP_RANGE_REGEX, target)):
            return TargetType.IP_RANGE
        try:
            socket.gethostbyname(target)  # Check if target is a Domain
            return TargetType.DOMAIN
        except socket.gaierror:
            pass
        logger.warning(f"[Security] Invalid target {target}")
        # Target is invalid or target type is not supported
        raise ValidationError(
            {
                "target": f"Invalid target {target}. IP address, IP range or domain is required"
            }
        )

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        return {
            InputKeyword.TARGET.name.lower(): self.target,
            InputKeyword.HOST.name.lower(): self.target,
            InputKeyword.URL.name.lower(): self._get_url(self.target),
        }

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.target

    def get_project(self) -> Project:
        """Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        """
        return self.project

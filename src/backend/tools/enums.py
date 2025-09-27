"""Enumeration classes for tools module configuration and constants.

Defines enum classes for tool execution intensity levels and security testing
stages used throughout the tools system for categorization and workflow control.
"""

from django.db import models
from django.db.models.enums import Choices


class Intensity(models.IntegerChoices):
    """Enumeration for tool execution intensity levels.

    Defines intensity levels that control tool execution thoroughness,
    performance characteristics, and resource usage. Higher intensity
    levels typically result in more comprehensive scanning but increased
    execution time and system resource consumption.
    """

    SNEAKY = 1  # Softest
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5  # Hardest


class Stage(models.IntegerChoices):
    """Enumeration for security testing stages and workflow phases.

    Defines the sequential stages of security testing workflows, enabling
    proper tool orchestration and dependency management. Stages represent
    the logical progression of security assessment activities.
    """

    OSINT = 1
    ENUMERATION = 2
    VULNERABILITIES = 3
    SERVICES = 4
    EXPLOITATION = 5


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Intensity: type[Choices] = Intensity
Stage: type[Stage] = Stage

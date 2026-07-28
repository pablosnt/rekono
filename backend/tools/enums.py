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

    Attributes:
        SNEAKY (int): Slowest and most stealthy intensity, minimizing detection risk
        LOW (int): Cautious intensity, faster than SNEAKY but still conservative
        NORMAL (int): Default, balanced intensity used by most tool configurations
        HARD (int): Aggressive intensity, favoring speed and thoroughness over stealth
        INSANE (int): Fastest and most aggressive intensity, prioritizing speed above all else
    """

    SNEAKY = 1
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5


class Stage(models.IntegerChoices):
    """Enumeration for security testing stages and workflow phases.

    Defines the sequential stages of security testing workflows, enabling
    proper tool orchestration and dependency management. Stages represent
    the logical progression of security assessment activities.

    Attributes:
        OSINT (int): Open-source intelligence gathering about the target, including
                    name resolution and subdomain discovery
        ENUMERATION (int): Discovery of hosts, ports, and network services
        VULNERABILITIES (int): Vulnerability scanning against what has been discovered
        SERVICES (int): In-depth testing of a specific discovered service, such as a
                       web application, a TLS configuration, or an SSH server
        EXPLOITATION (int): Exploit research for the findings already identified
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

"""Options that define how and when a tool is run."""

from django.db import models
from django.db.models.enums import Choices


class Intensity(models.IntegerChoices):
    """How aggressive an execution is, from the stealthiest to the fastest.

    Each tool maps the intensities that it supports to its own arguments, so the
    users can choose how noisy a scan is without knowing those arguments.
    """

    SNEAKY = 1
    LOW = 2
    NORMAL = 3
    HARD = 4
    INSANE = 5


class Stage(models.IntegerChoices):
    """Phase of the assessment that a tool configuration belongs to.

    The stages define the order in which the configurations of a process are run,
    since each one works from what the previous ones discovered.

    Attributes:
        OSINT: Data gathered from public sources, like the subdomains of a domain.
        ENUMERATION: Discovery of the hosts, the ports, and their services.
        VULNERABILITIES: Vulnerability scanning of what was discovered.
        SERVICES: Deep testing of one service, like a web application or a TLS
          configuration.
        EXPLOITATION: Search of the exploits available for the vulnerabilities.
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

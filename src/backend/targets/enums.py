from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db import models


class TargetType(models.TextChoices, Enum):
    """Supported target types."""

    PRIVATE_IP = "Private IP"
    PUBLIC_IP = "Public IP"
    NETWORK = "Network"
    IP_RANGE = "IP range"
    DOMAIN = "Domain"

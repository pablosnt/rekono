from django.db import models
from django.db.models.enums import Choices


class TargetType(models.TextChoices):
    """Supported target types."""

    PRIVATE_IP = "Private IP"
    PUBLIC_IP = "Public IP"
    NETWORK = "Network"
    IP_RANGE = "IP range"
    DOMAIN = "Domain"


TargetType: type[Choices] = TargetType  # https://github.com/google/pytype/issues/1048

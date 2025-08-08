from django.db import models
from django.db.models.enums import Choices


class TargetType(models.TextChoices):
    PRIVATE_IP = "Private IP"
    PUBLIC_IP = "Public IP"
    NETWORK = "Network"
    IP_RANGE = "IP range"
    DOMAIN = "Domain"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
TargetType: type[Choices] = TargetType

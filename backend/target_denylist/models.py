"""Model of the denylist entries that keep Rekono away from some targets."""

from django.db import models

from framework.models import BaseModel
from security.validators.input_validator import Regex, Validator


class TargetDenylist(BaseModel):
    """Target that can't be scanned, as an exact value, a regex, or an IP network.

    Attributes:
        target: Value that the denied targets must match.
        default: Whether the entry is one of the ones that Rekono provides, which
          means that it can't be updated or removed by the administrators.
        blocked: Number of times that this entry denied a target.
    """

    target = models.TextField(unique=True, max_length=100, validators=[Validator(Regex.TARGET_REGEX)])
    default = models.BooleanField(default=False)
    blocked = models.IntegerField(default=0)

    def __str__(self) -> str:
        """Return the value of the denylist entry."""
        return self.target

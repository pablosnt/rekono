from django.db import models
from framework.models import BaseModel
from security.validators.input_validator import Regex, Validator

# Create your models here.


class TargetBlacklist(BaseModel):
    target = models.TextField(
        unique=True, max_length=100, validators=[Validator(Regex.TARGET_REGEX.value)]
    )
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.target

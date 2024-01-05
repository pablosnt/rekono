from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseLike, BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from tools.models import Configuration

# Create your models here.


class Process(BaseLike):
    name = models.TextField(
        max_length=100,
        unique=True,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    description = models.TextField(
        max_length=300, validators=[Validator(Regex.TEXT.value, code="description")]
    )
    owner = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    tags = TaggableManager()

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.name


class Step(BaseModel):
    process = models.ForeignKey(Process, related_name="steps", on_delete=models.CASCADE)
    configuration = models.ForeignKey(
        Configuration, on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["process", "configuration"], name="unique_step"
            )
        ]

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.process.__str__()} - {self.configuration.__str__()}"

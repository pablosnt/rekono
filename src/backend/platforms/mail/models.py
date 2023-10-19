from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from framework.models import BaseModel
from security.utils.input_validator import Regex, Validator

# Create your models here.


class SMTPSettings(BaseModel):
    host = models.TextField(
        max_length=100,
        validators=[Validator(Regex.TARGET.value)],
        blank=True,
        null=True,
    )
    port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)],
        blank=True,
        null=True,
        default=587,
    )
    username = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
        null=True,
        blank=True,
    )
    # TODO: encrypt and decrypt secret for more security
    password = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
    )
    tls = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

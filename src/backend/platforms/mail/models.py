from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator

# Create your models here.


class SMTPSettings(BaseEncrypted):
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
    _password = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
        db_column="password",
    )
    tls = models.BooleanField(default=True)

    _encrypted_field = "_password"

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

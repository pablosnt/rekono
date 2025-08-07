from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator


class SMTPSettings(BaseEncrypted):
    host = models.TextField(max_length=100, validators=[Validator(Regex.TARGET)], blank=True, null=True)
    port = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(65535)], blank=True, null=True, default=587
    )
    username = models.TextField(max_length=100, validators=[Validator(Regex.NAME, code="name")], null=True, blank=True)
    _password = models.TextField(
        max_length=200,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="password",
    )
    tls = models.BooleanField(default=True)

    _encrypted_field = "_password"

    def __str__(self) -> str:
        return f"{self.host}:{self.port}" if self.host and self.port else "None"

from django.db import models
from rest_framework.authtoken.models import Token

from framework.models import BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import (
    FutureDatetimeValidator,
    Regex,
    Validator,
)


class ApiToken(Token, BaseModel):
    key = models.CharField(max_length=128, unique=True)
    name = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="api_tokens",
        on_delete=models.CASCADE,
    )
    expiration = models.DateTimeField(blank=True, null=True, validators=[FutureDatetimeValidator(code="expiration")])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "user"], name="unique_api_token")]

    @classmethod
    def generate_key(cls):
        key = Token.generate_key()
        return Token.generate_key() if ApiToken.objects.filter(key=key).exists() else key

    def __str__(self) -> str:
        return f"{self.user.__str__()} - {self.name}"

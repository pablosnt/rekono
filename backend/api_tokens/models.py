"""Model of the API tokens used to consume the Rekono API."""

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
    """Token that authenticates the requests performed by an external client.

    Extends the DRF token with a name, so a user can tell their tokens apart, and
    with an expiration date.

    Attributes:
        key: Hash of the token value, since the value itself is never stored.
        name: Name given by the user to identify this token.
        user: User that owns the token, and whose permissions it grants.
        expiration: Date when the token stops being valid, or None to never expire.
    """

    key = models.CharField(max_length=128, unique=True)
    name = models.TextField(max_length=100, validators=[Validator(Regex.NAME, code="name")])
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="api_tokens",
        on_delete=models.CASCADE,
    )
    expiration = models.DateTimeField(blank=True, null=True, validators=[FutureDatetimeValidator(code="expiration")])

    class Meta:
        """Model configuration, requiring a unique token name for each user."""

        constraints = [models.UniqueConstraint(fields=["name", "user"], name="unique_api_token")]

    @classmethod
    def generate_key(cls):
        """Generate a token value that isn't used by any other API token."""
        key = Token.generate_key()
        return cls.generate_key() if ApiToken.objects.filter(key=key).exists() else key

    def __str__(self) -> str:
        """Return the user that owns the token and the name of the token."""
        return f"{self.user.__str__()} - {self.name}"

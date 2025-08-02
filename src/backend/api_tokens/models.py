"""Models for API tokens with secure generation and validation.

Provides the ApiToken model for managing user API tokens with security features
including unique key generation, expiration validation, and proper constraints.
"""

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
    """Model representing a secure API token for user authentication.

    Extends Django REST Framework's Token model with additional security features
    including named tokens, expiration dates, and unique key generation.

    Attributes:
        key (CharField): Unique 128-character token identifier
        name (TextField): User-defined name for the token (max 100 chars)
        user (ForeignKey): The user who owns this token
        expiration (DateTimeField): Optional token expiration date

    Example:
        Create a new API token:
        
        ```python
        from datetime import datetime, timedelta
        token = ApiToken.objects.create(
            name="My API Token",
            user=user,
            expiration=datetime.now() + timedelta(days=30)
        )
        ```
    """

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
        """Generate a unique API token key.

        Recursively generates keys until a unique one is found to prevent
        collisions in the database.

        Returns:
            str: A unique 40-character hexadecimal token key
        """
        key = Token.generate_key()
        return cls.generate_key() if ApiToken.objects.filter(key=key).exists() else key

    def __str__(self) -> str:
        """Return a string representation of the API token.

        Returns:
            str: String in format "username - token_name"
        """
        return f"{self.user.__str__()} - {self.name}"

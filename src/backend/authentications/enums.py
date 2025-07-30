"""Authentication type enumerations for Rekono.

This module defines the available authentication types that can be used
for storing and managing authentication credentials in the system.
"""

from django.db import models
from django.db.models.enums import Choices


class AuthenticationType(models.TextChoices):
    """Enumeration of supported authentication types.

    This class defines the different types of authentication methods
    that can be used for storing credentials in the system.

    Attributes:
        BASIC (str): Basic authentication using username and password.
        BEARER (str): Bearer token authentication.
        COOKIE (str): Cookie-based authentication.
        DIGEST (str): Digest authentication.
        JWT (str): JSON Web Token authentication.
        NTLM (str): NTLM authentication.
        TOKEN (str): Generic token-based authentication.
    """

    BASIC = "Basic"
    BEARER = "Bearer"
    COOKIE = "Cookie"
    DIGEST = "Digest"
    JWT = "JWT"
    NTLM = "NTLM"
    TOKEN = "Token"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
AuthenticationType: type[Choices] = AuthenticationType

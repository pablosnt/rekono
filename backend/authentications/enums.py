"""Authentication types supported by the credentials."""

from django.db import models
from django.db.models.enums import Choices


class AuthenticationType(models.TextChoices):
    """Way in which a credential is sent to the target service.

    The type is provided to the tools as an input keyword, so they can build the
    authentication header or parameter that the service expects.
    """

    BASIC = "Basic"
    BEARER = "Bearer"
    COOKIE = "Cookie"
    DIGEST = "Digest"
    JWT = "JWT"
    NTLM = "NTLM"
    TOKEN = "Token"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
AuthenticationType: type[Choices] = AuthenticationType

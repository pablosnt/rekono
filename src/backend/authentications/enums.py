from django.db import models
from django.db.models.enums import Choices


class AuthenticationType(models.TextChoices):
    """Supported authentication types."""

    BASIC = "Basic"
    BEARER = "Bearer"
    COOKIE = "Cookie"
    DIGEST = "Digest"
    JWT = "JWT"
    NTLM = "NTLM"
    TOKEN = "Token"


AuthenticationType: type[Choices] = AuthenticationType  # https://github.com/google/pytype/issues/1048

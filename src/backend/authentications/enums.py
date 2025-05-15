# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db import models


class AuthenticationType(models.TextChoices):
    """Supported authentication types."""

    BASIC = "Basic"
    BEARER = "Bearer"
    COOKIE = "Cookie"
    DIGEST = "Digest"
    JWT = "JWT"
    NTLM = "NTLM"
    TOKEN = "Token"

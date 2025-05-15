# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db import models


class WordlistType(models.TextChoices):
    """Wordlist type names."""

    ENDPOINT = "Endpoint"
    SUBDOMAIN = "Subdomain"

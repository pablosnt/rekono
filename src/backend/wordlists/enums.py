from django.db import models
from django.db.models.enums import Choices


class WordlistType(models.TextChoices):
    """Wordlist type names."""

    ENDPOINT = "Endpoint"
    SUBDOMAIN = "Subdomain"


WordlistType: type[Choices] = WordlistType  # https://github.com/google/pytype/issues/1048

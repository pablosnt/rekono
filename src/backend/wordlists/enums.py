from django.db import models
from django.db.models.enums import Choices


class WordlistType(models.TextChoices):
    ENDPOINT = "Endpoint"
    SUBDOMAIN = "Subdomain"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
WordlistType: type[Choices] = WordlistType

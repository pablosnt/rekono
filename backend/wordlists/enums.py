"""Types of wordlists that the tools can use."""

from django.db import models
from django.db.models.enums import Choices


class WordlistType(models.TextChoices):
    """Kind of data that a wordlist contains.

    The type decides which tools can use a wordlist, since a tool that discovers
    paths can't do anything with a list of subdomains.
    """

    ENDPOINT = "Endpoint"
    SUBDOMAIN = "Subdomain"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
WordlistType: type[Choices] = WordlistType

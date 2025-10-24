"""Enumeration classes for wordlist types and categories.

Defines enumeration values used throughout the wordlist management system
for categorizing different types of wordlists based on their intended use.
"""

from django.db import models
from django.db.models.enums import Choices


class WordlistType(models.TextChoices):
    """Enumeration of supported wordlist types for security testing.

    Defines the available categories of wordlists based on their intended use
    in security tools and testing scenarios.

    Attributes:
        ENDPOINT (str): Wordlists for endpoint/directory enumeration and brute-forcing
        SUBDOMAIN (str): Wordlists for subdomain discovery and enumeration
    """

    ENDPOINT = "Endpoint"
    SUBDOMAIN = "Subdomain"


# Type annotation fix for pytype compatibility
# https://github.com/google/pytype/issues/1048
WordlistType: type[Choices] = WordlistType

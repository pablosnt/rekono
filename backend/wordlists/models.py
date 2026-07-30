"""Wordlist models for Rekono.

Defines the Wordlist model for managing file-based wordlists used in security testing.
Supports secure file storage, integrity validation, and integration with security
tools requiring input datasets for enumeration and brute-force operations.
"""

from pathlib import Path
from typing import Any

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput, BaseLike
from rekono.settings import AUTH_USER_MODEL
from security.file_handler import FileHandler
from security.validators.input_validator import Regex, Validator
from targets.models import Target
from wordlists.enums import WordlistType


class Wordlist(BaseInput, BaseLike):
    """Model representing file-based wordlists for security testing tools.

    Represents wordlists used by security tools for enumeration, directory brute-forcing,
    subdomain discovery, and other automated testing scenarios. Provides secure file
    management with integrity validation, user ownership, and integration capabilities.

    Attributes:
        name (TextField): Unique name for the wordlist (max 100 characters)
        type (TextField): Wordlist type from WordlistType enum (max 10 characters)
        path (TextField): File system path to the wordlist file (unique, max 200 characters)
        checksum (TextField): SHA-512 checksum for file integrity verification (optional, max 128 characters)
        size (IntegerField): Number of entries in the wordlist file (auto-calculated)
        owner (ForeignKey): User who uploaded/owns this wordlist (optional)

    Example:
        Create a new wordlist for subdomain enumeration:

        ```python
        wordlist = Wordlist.objects.create(
            name="Common Subdomains",
            type=WordlistType.SUBDOMAIN,
            path="/path/to/subdomains.txt",
            owner=user
        )
        ```
    """

    name = models.TextField(max_length=100, unique=True, validators=[Validator(Regex.NAME, code="name")])
    type = models.TextField(max_length=10, choices=WordlistType.choices)
    path = models.TextField(max_length=200, unique=True)
    checksum = models.TextField(max_length=128, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    _filters = [BaseInput.Filter(type=WordlistType, field="type")]
    _parse_mapping = {InputKeyword.WORDLIST: "path"}

    def filter(self, argument_input: Any, target: Target | None = None) -> bool:
        """Filter wordlist availability based on file existence and integrity.

        Validates that the wordlist file exists on the file system and, if a checksum
        is available, verifies the file integrity. This ensures only valid wordlists
        are used by security tools during execution.

        Args:
            argument_input (Any): Input configuration for filtering
            target (Target | None): Target object for context-specific filtering

        Returns:
            bool: True if wordlist is available and valid, False otherwise
        """
        check = Path(self.path).is_file()
        # Bundled default wordlists have no checksum, so integrity is only verified when one is stored
        if check and self.checksum:
            check = check and FileHandler().validate_filepath_checksum(self.path, self.checksum)
        if argument_input.filter:
            return super().filter(argument_input, target) and check
        return check

    def __str__(self) -> str:
        """Return string representation of the wordlist.

        Returns:
            str: The name of the wordlist
        """
        return self.name

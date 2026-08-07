"""Model of the wordlists that the tools use."""

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
    """List of words stored in a file that the tools use to enumerate.

    Attributes:
        name: Name that identifies the wordlist.
        type: Kind of data that the wordlist contains.
        path: Location of the wordlist file, which is what the tools receive.
        checksum: Checksum of the file content, only for the uploaded wordlists.
        size: Number of words in the file.
        owner: User that uploaded the wordlist, or nobody for the default ones.
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
        """Check if this wordlist can be used as input for an argument.

        Args:
            argument_input: Tool input whose filter conditions must be matched.
            target: Target of the execution, unused because a wordlist is a file
              and doesn't belong to any target.

        Returns:
            Whether the wordlist matches the argument input and its file is still
            available and hasn't been modified since it was uploaded.
        """
        check = Path(self.path).is_file()
        # Bundled default wordlists have no checksum, so integrity is only verified when one is stored
        if check and self.checksum:
            check = check and FileHandler().validate_filepath_checksum(self.path, self.checksum)
        if argument_input.filter:
            return super().filter(argument_input, target) and check
        return check

    def __str__(self) -> str:
        """Return the name of the wordlist."""
        return self.name

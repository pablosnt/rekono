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
    name = models.TextField(max_length=100, unique=True, validators=[Validator(Regex.NAME, code="name")])
    type = models.TextField(max_length=10, choices=WordlistType.choices)
    path = models.TextField(max_length=200, unique=True)
    checksum = models.TextField(max_length=128, blank=True, null=True)
    # Number of entries in the wordlist file
    size = models.IntegerField(blank=True, null=True)
    # User that created the wordlist
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    filters = [BaseInput.Filter(type=WordlistType, field="type")]
    parse_mapping = {InputKeyword.WORDLIST: "path"}

    def filter(self, input: Any, target: Target | None = None) -> bool:
        check = Path(self.path).is_file()  # Check if wordlist file exists
        if check and self.checksum:  # If checksum exists, verifies it
            check = check and FileHandler().validate_filepath_checksum(self.path, self.checksum)
        if input.filter:
            return super().filter(input, target) and check
        return check

    def __str__(self) -> str:
        return self.name

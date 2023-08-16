import os
from typing import Any, Dict

from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput

# from likes.models import LikeBase
from security.file_handler import FileHandler
from security.input_validation import Regex, Validator
from wordlists.enums import WordlistType

# Create your models here.


class Wordlist(BaseInput):
    name = models.TextField(
        max_length=100,
        unique=True,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    type = models.TextField(max_length=10, choices=WordlistType.choices)
    path = models.TextField(max_length=200, unique=True)
    checksum = models.TextField(max_length=128, blank=True, null=True)
    # Number of entries in the wordlist file
    size = models.IntegerField(blank=True, null=True)
    # User that created the wordlist
    # creator = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    # )

    filters = [BaseInput.Filter(type=WordlistType, field="type")]

    def filter(self, input: Any) -> bool:
        """Check if this instance is valid based on input filter.

        Args:
            input (Any): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        """
        check = os.path.isfile(self.path)  # Check if wordlist file exists
        if check and self.checksum:  # If checksum exists
            check = check and FileHandler().validate_filepath_checksum(
                self.path, self.checksum
            )
        if input.filter:  # If input filter is established
            return super().filter(input) and check
        return check

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        return {InputKeyword.WORDLIST.name.lower(): self.path}

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.name

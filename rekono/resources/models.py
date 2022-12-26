import os
from typing import Any, Dict, cast

from django.conf import settings
from django.db import models
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from likes.models import LikeBase
from security.file_upload import check_checksum
from security.input_validation import validate_name
from tools.models import Input

from resources.enums import WordlistType

# Create your models here.


class Wordlist(LikeBase, BaseInput):
    '''Wordlist model.'''

    name = models.TextField(max_length=100, unique=True, validators=[validate_name])                # Wordlist name
    type = models.TextField(max_length=10, choices=WordlistType.choices)        # Wordlist type
    path = models.TextField(max_length=200, unique=True)                        # Wordlist file path
    checksum = models.TextField(max_length=128, blank=True, null=True)          # Wordlist file hash
    size = models.IntegerField(blank=True, null=True)                           # Number of entries in the wordlist file
    # User that created the wordlist
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        check = os.path.isfile(self.path)                                       # Check if wordlist file exists
        if check and self.checksum:                                             # If checksum exists
            check = check and check_checksum(self.path, self.checksum)          # Check wordlist file hash
        if input.filter:                                                        # If input filter is established
            # Check wordlist type
            check = check and self.type == cast(Dict[str, str], WordlistType)[input.filter.upper()]
        return check

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        return {InputKeyword.WORDLIST.name.lower(): self.path}

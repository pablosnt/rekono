import os
from typing import Any, Dict

from django.conf import settings
from django.db import models
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from likes.models import LikeBase
from resources.enums import WordlistType
from security.file_upload import check_checksum
from security.input_validation import validate_name
from tools.models import Input

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

    class Meta:
        '''Model metadata.'''

        ordering = ['-id']                                                      # Default ordering for pagination

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.name

    def get_project(self) -> Any:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Any: Related project entity
        '''
        return None

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        exist = os.path.isfile(self.path)                                       # Check if wordlist file exists
        if exist and self.checksum:                                             # If checksum exists
            return check_checksum(self.path, self.checksum)                     # Check wordlist file hash
        return exist

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        return {InputKeyword.WORDLIST.name.lower(): self.path}

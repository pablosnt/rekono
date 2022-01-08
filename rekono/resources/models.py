import os
from typing import Any

from django.conf import settings
from django.db import models
from inputs.base import BaseInput
from inputs.enums import InputKeyword
from likes.models import LikeBase
from resources.enums import WordlistType
from security.file_upload import check_checksum
from tools.models import Input

# Create your models here.


class Wordlist(LikeBase, BaseInput):
    name = models.TextField(max_length=50, unique=True)
    type = models.TextField(max_length=10, choices=WordlistType.choices)
    path = models.TextField(max_length=200, unique=True)
    checksum = models.TextField(max_length=128, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

    def get_project(self) -> Any:
        return None
    
    def filter(self, input: Input) -> bool:
        exist = os.path.isfile(self.path)
        if exist and self.checksum:
            return check_checksum(self.path, self.checksum)
        return exist

    def parse(self, accumulated: dict = {}) -> dict:
        return {
            InputKeyword.WORDLIST.name.lower(): self.path
        }

from typing import Any

from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseLike
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class Note(BaseLike):
    project = models.ForeignKey(
        Project, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    target = models.ForeignKey(
        Target, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.TextField(
        max_length=200, validators=[Validator(Regex.NAME.value, code="title")]
    )
    body = models.TextField(validators=[Validator(Regex.TEXT.value, code="body")])
    tags = TaggableManager()
    owner = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    public = models.BooleanField(default=False)
    forked_from = models.ForeignKey(
        "Note",
        related_name="forks",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        value = ""
        for item in [self.target, self.project]:
            if item:
                value = f"{item.__str__()} - "
                break
        return f"{value}{self.title}"

    def get_project(self) -> Any:
        return self.target.project if self.target else self.project

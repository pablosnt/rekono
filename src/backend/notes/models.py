from typing import Any

from django.db import models
from executions.models import Execution
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from framework.models import BaseLike
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from taggit.managers import TaggableManager
from targets.models import Target
from tasks.models import Task


class Note(BaseLike):
    project = models.ForeignKey(Project, related_name="notes", on_delete=models.CASCADE)
    target = models.ForeignKey(
        Target, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    task = models.ForeignKey(
        Task, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    execution = models.ForeignKey(
        Execution, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    osint = models.ForeignKey(
        OSINT, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    host = models.ForeignKey(
        Host, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    port = models.ForeignKey(
        Port, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    path = models.ForeignKey(
        Path, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    credential = models.ForeignKey(
        Credential,
        related_name="notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    technology = models.ForeignKey(
        Technology,
        related_name="notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    vulnerability = models.ForeignKey(
        Vulnerability,
        related_name="notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    exploit = models.ForeignKey(
        Exploit,
        related_name="notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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

    @classmethod
    def get_project_field(cls) -> str:
        return "project"

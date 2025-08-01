"""Note models for managing user annotations and documentation in Rekono.

This module provides the Note model which allows users to create annotations,
documentation, and comments on various entities within the Rekono system.
Notes can be attached to projects, targets, tasks, executions, and various
finding types, supporting a flexible annotation system with tagging and
forking capabilities.
"""

from django.db import models
from taggit.managers import TaggableManager

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
from targets.models import Target
from tasks.models import Task


class Note(BaseLike):
    """Model for user-created notes and annotations.

    This model represents user-created notes that can be attached to various
    entities within the Rekono system. Notes support rich content with titles,
    bodies, tags, and can be made public or private. They also support forking
    functionality, allowing users to create copies of public notes.

    Notes can be associated with multiple entity types through optional foreign
    key relationships. Only one entity relationship should be active at a time,
    and the system automatically determines the project context from the related
    entity.

    The model inherits from BaseLike, providing like/unlike functionality for
    social features.

    Attributes:
        project: The project this note belongs to (required).
        target: Optional target this note is associated with.
        task: Optional task this note is associated with.
        execution: Optional execution this note is associated with.
        osint: Optional OSINT finding this note is associated with.
        host: Optional host finding this note is associated with.
        port: Optional port finding this note is associated with.
        path: Optional path finding this note is associated with.
        credential: Optional credential finding this note is associated with.
        technology: Optional technology finding this note is associated with.
        vulnerability: Optional vulnerability finding this note is associated with.
        exploit: Optional exploit finding this note is associated with.
        title: The note's title (max 200 characters, validated).
        body: The note's content body (optional).
        tags: Tags associated with the note (using django-taggit).
        owner: The user who created the note.
        public: Whether the note is publicly visible to project members.
        forked_from: Reference to the original note if this is a fork.
        created_at: Timestamp when the note was created.
        updated_at: Timestamp when the note was last updated.
    """

    project = models.ForeignKey(Project, related_name="notes", on_delete=models.CASCADE)
    target = models.ForeignKey(Target, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    execution = models.ForeignKey(Execution, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    osint = models.ForeignKey(OSINT, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey(Host, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    port = models.ForeignKey(Port, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    path = models.ForeignKey(Path, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
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
    title = models.TextField(max_length=200, validators=[Validator(Regex.NAME.value, code="title")])
    body = models.TextField(blank=True, null=True)
    tags = TaggableManager()
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
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

    _project_field = "project"

    def __str__(self) -> str:
        """Return string representation of the note.

        Creates a descriptive string by combining the target, project, and title
        in a readable format, filtering out any None values.

        Returns:
            A string representation in format "target - project - title".
        """
        item = next(
            iter(
                [
                    link
                    for link in [
                        self.target,
                        self.task,
                        self.execution,
                        self.osint,
                        self.host,
                        self.port,
                        self.path,
                        self.credential,
                        self.technology,
                        self.vulnerability,
                        self.exploit,
                    ]
                    if link
                ]
            )
        )
        if not item:
            item = self.project
        return " - ".join([item.__str__(), self.title])

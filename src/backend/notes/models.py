"""Django models for notes and documentation management.

This module provides the core data models for Rekono's note-taking and documentation
system, which enables security teams to capture, organize, and share insights throughout
security assessments. The notes system supports contextual attachment to any entity
in the assessment workflow with collaborative features including forking, tagging,
and community-driven curation through likes.

Architecture:
    The notes system uses a flexible association model where notes can be attached
    to any entity type (projects, targets, tasks, executions, findings) through
    foreign key relationships. Only one association per note is allowed, ensuring
    clear context. The system supports both individual and collaborative workflows
    with sharing and forking capabilities for knowledge base development.
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
    """Model representing contextual notes and documentation for security assessments.

    Represents user-generated documentation that can be attached to any entity within
    the security assessment workflow. Supports collaborative features including public
    sharing, forking for knowledge base development, tagging for organization, and
    like functionality for community-driven content curation.

    Collaborative Features:
        - Public/Private visibility controls for team sharing
        - Note forking system for knowledge base development
        - Tagging system for organization and categorization
        - Like/unlike functionality for content curation

    Attributes:
        project (ForeignKey): The project this note belongs to (required)
        target (ForeignKey): Associated target entity (optional)
        task (ForeignKey): Associated task entity (optional)
        execution (ForeignKey): Associated execution entity (optional)
        osint (ForeignKey): Associated OSINT finding entity (optional)
        host (ForeignKey): Associated host finding entity (optional)
        port (ForeignKey): Associated port finding entity (optional)
        path (ForeignKey): Associated path finding entity (optional)
        credential (ForeignKey): Associated credential finding entity (optional)
        technology (ForeignKey): Associated technology finding entity (optional)
        vulnerability (ForeignKey): Associated vulnerability finding entity (optional)
        exploit (ForeignKey): Associated exploit finding entity (optional)
        title (TextField): Note title with validation (max 200 chars)
        body (TextField): Note content body (optional)
        tags (TaggableManager): Tag system for organization and search
        owner (ForeignKey): The user who created this note
        public (BooleanField): Whether note is visible to all project members
        forked_from (ForeignKey): Reference to original note if this is a fork
        created_at (DateTimeField): Note creation timestamp
        updated_at (DateTimeField): Note last modification timestamp

    Example:
        Create a vulnerability-specific note:

        ```python
        note = Note.objects.create(
            project=project,
            vulnerability=vuln_finding,
            title="SQL Injection Analysis",
            body="Detailed analysis of the SQL injection vulnerability...",
            owner=user,
            public=True
        )
        ```
    """

    project = models.ForeignKey(Project, related_name="notes", on_delete=models.CASCADE)
    target = models.ForeignKey(Target, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    execution = models.ForeignKey(Execution, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    osint = models.ForeignKey(OSINT, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey(Host, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    port = models.ForeignKey(Port, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    path = models.ForeignKey(Path, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    credential = models.ForeignKey(Credential, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    technology = models.ForeignKey(Technology, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    vulnerability = models.ForeignKey(
        Vulnerability, related_name="notes", on_delete=models.CASCADE, null=True, blank=True
    )
    exploit = models.ForeignKey(Exploit, related_name="notes", on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(max_length=200, validators=[Validator(Regex.NAME.value, code="title")])
    body = models.TextField(blank=True, null=True)
    tags = TaggableManager()
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    public = models.BooleanField(default=False)
    forked_from = models.ForeignKey("Note", related_name="forks", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _project_field = "project"

    def __str__(self) -> str:
        """Return string representation of the note.

        Constructs a string representation by finding the associated entity
        (target, task, execution, or finding) and combining it with the note title.
        Falls back to project if no specific entity association exists.

        Returns:
            str: String in format "associated_entity - title" or "project - title"
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

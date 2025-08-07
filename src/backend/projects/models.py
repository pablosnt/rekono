"""Project models for Rekono's security testing engagements.

Defines the Project model for organizing security testing activities into
discrete engagement workspaces. Projects provide multi-tenant isolation,
team collaboration features, and centralized management of security testing
resources including targets, executions, and findings.
"""

from functools import cached_property
from typing import Self

from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator


class Project(BaseModel):
    """Model representing a security testing project engagement.

    Represents a security testing project that serves as the organizational unit
    for all security testing activities. Projects enable team collaboration with
    member management, provide access control boundaries, and integrate with
    external vulnerability management platforms for comprehensive security testing.

    Attributes:
        name (TextField): Unique project name identifier (max 100 chars)
        description (TextField): Project description and context (max 300 chars)
        owner (ForeignKey): The user who created and owns this project
        members (ManyToManyField): Team members with project access permissions
        tags (TaggableManager): Organizational tags for project categorization

    Example:
        Create a new security testing project:

        ```python
        project = Project.objects.create(
            name="Web Application Security Assessment",
            description="Security testing for customer web application",
            owner=user
        )
        project.members.add(team_member)
        project.tags.add("web", "external")
        ```
    """

    name = models.TextField(
        max_length=100,
        unique=True,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    description = models.TextField(max_length=300, validators=[Validator(Regex.TEXT.value, code="description")])
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    members = models.ManyToManyField(AUTH_USER_MODEL, related_name="projects", blank=True)
    tags = TaggableManager()  # Project tags

    def __str__(self) -> str:
        """Return string representation of the project.

        Returns:
            str: The project name for display and logging purposes.
        """
        return self.name

    @cached_property
    def parent_project(self) -> Self:
        """Get the parent project reference for access control operations.

        Returns the project itself as the root access control boundary for
        all security testing resources associated with this project.

        Returns:
            Self: The project instance serving as the access control parent.
        """
        return self

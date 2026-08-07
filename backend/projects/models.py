"""Model of the projects where the security assessments are organized."""

from functools import cached_property
from typing import Self

from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator


class Project(BaseModel):
    """Workspace that groups the targets, tasks, and findings of an assessment.

    Attributes:
        name: Name of the project, unique in the whole platform.
        description: Description of the assessment that the project covers.
        owner: User that created the project.
        members: Users that can access the data of the project.
        tags: Labels that the users assign to organize their projects.
    """

    name = models.TextField(max_length=100, unique=True, validators=[Validator(Regex.NAME, code="name")])
    description = models.TextField(max_length=300, validators=[Validator(Regex.TEXT, code="description")])
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    members = models.ManyToManyField(AUTH_USER_MODEL, related_name="projects", blank=True)
    tags = TaggableManager()

    def __str__(self) -> str:
        """Return the name of the project."""
        return self.name

    @cached_property
    def parent_project(self) -> Self:
        """The project itself, since it's the root of the project scoping."""
        return self

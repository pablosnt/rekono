from typing import Any

from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator

# Create your models here.


class Project(BaseModel):
    """Project model."""

    name = models.TextField(
        max_length=100,
        unique=True,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    description = models.TextField(
        max_length=300, validators=[Validator(Regex.TEXT.value, code="description")]
    )
    # User that created the project
    owner = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    # Relation with all users that belong to the project
    members = models.ManyToManyField(
        AUTH_USER_MODEL, related_name="projects", blank=True
    )
    tags = TaggableManager()  # Project tags

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.name

    def get_project(self) -> Any:
        """Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Any: Related project entity
        """
        return self

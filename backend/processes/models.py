"""Django models for process management and workflow configuration.

This module provides the core data models for Rekono's process management system,
which enables security teams to create and manage complex security testing workflows.
The process system supports multi-step security assessments with tool chaining,
dependency management, and community-driven process sharing capabilities.

Architecture:
    The process system uses a hierarchical approach where processes contain multiple
    steps, each step references a tool configuration, and the system manages execution
    order and dependencies automatically. This design enables complex security testing
    workflows while maintaining flexibility and reusability.
"""

from django.db import models
from taggit.managers import TaggableManager

from framework.models import BaseLike, BaseModel
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from tools.models import Configuration


class Process(BaseLike):
    """Model representing a security testing workflow with multiple tool execution steps.

    Represents a complete security testing process that consists of multiple tool
    execution steps designed to perform comprehensive vulnerability assessments.
    Processes support community sharing through the like system, tagging for
    categorization, and ownership management for access control.

    Attributes:
        name (TextField): Unique process name for identification (max 100 chars)
        description (TextField): Detailed process description (max 500 chars)
        owner (ForeignKey): The user who created this process (optional)
        tags (TaggableManager): Tag system for process categorization
        steps (RelatedManager): Related Step objects defining the workflow

    Example:
        Create a reconnaissance process with multiple steps:

        ```python
        process = Process.objects.create(
            name="Web Application Reconnaissance",
            description="Complete web app discovery and enumeration workflow",
            owner=user
        )
        process.tags.add("reconnaissance", "web", "automation")
        ```
    """

    name = models.TextField(max_length=100, unique=True, validators=[Validator(Regex.NAME, code="name")])
    description = models.TextField(max_length=500, validators=[Validator(Regex.TEXT, code="description")])
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    tags = TaggableManager()

    def __str__(self) -> str:
        """Return string representation of the process.

        Returns:
            str: The process name.
        """
        return self.name


class Step(BaseModel):
    """Model representing a single tool execution step within a security process.

    Represents an individual step in a security testing process that defines
    which tool configuration to execute. Steps within a process are planned
    and executed based on dependencies inferred from their configuration's
    input and output types, so independent steps can run in parallel while
    dependent ones wait for their prerequisites. Steps form the building
    blocks of complex security testing workflows.

    Attributes:
        process (ForeignKey): The parent process containing this step
        configuration (ForeignKey): Tool configuration to execute in this step (optional)

    Example:
        Add a port scanning step to a process:

        ```python
        step = Step.objects.create(
            process=reconnaissance_process,
            configuration=nmap_config
        )
        ```
    """

    process = models.ForeignKey(Process, related_name="steps", on_delete=models.CASCADE)
    configuration = models.ForeignKey(
        Configuration,
        related_name="steps",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        """Meta configuration for Step model.

        Defines database constraints and configuration for the Step model to ensure
        data integrity and prevent duplicate step configurations within processes.

        Attributes:
            constraints (list): Database constraints including unique constraint for
                               process-configuration combinations to prevent duplicates
        """

        constraints = [models.UniqueConstraint(fields=["process", "configuration"], name="unique_step")]

    def __str__(self) -> str:
        """Return string representation of the step.

        Returns:
            str: String in format "process - configuration".
        """
        return f"{self.process.__str__()} - {self.configuration.__str__()}"

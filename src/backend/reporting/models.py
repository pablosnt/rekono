"""Django models for security report generation and management.

Defines the Report model for tracking security report generation lifecycle including
status tracking, format configuration, and project-level access control with support
for hierarchical project relationships and multi-format output generation.
"""

from functools import cached_property

from django.db import models

from framework.models import BaseModel
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from reporting.enums import ReportFormat, ReportStatus
from targets.models import Target
from tasks.models import Task


class Report(BaseModel):
    """Model representing security reports with generation tracking and access control.

    Represents security assessment reports with comprehensive lifecycle management
    from creation to completion. Supports multiple output formats and flexible
    scoping at project, target, or task levels with background processing capabilities.

    Report Lifecycle:
        PENDING -> READY/ERROR
        - Reports are created with PENDING status during background generation
        - Status updates to READY upon successful completion or ERROR on failure
        - Generated files are stored with secure access controls and unique naming

    Attributes:
        project (ForeignKey): Associated project for project-scoped reports (optional)
        target (ForeignKey): Associated target for target-scoped reports (optional)
        task (ForeignKey): Associated task for task-scoped reports (optional)
        status (TextField): Current report generation status (from ReportStatus enum)
        format (TextField): Output format specification (from ReportFormat enum)
        path (TextField): Generated report file path (max 300 chars, optional)
        user (ForeignKey): User who requested the report generation (optional)
        date (DateTimeField): Report creation timestamp (auto-generated)

    Example:
        Create a task-scoped PDF report:

        ```python
        report = Report.objects.create(
            task=security_task,
            format=ReportFormat.PDF,
            user=request.user
        )
        ```
    """

    project = models.ForeignKey(Project, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    target = models.ForeignKey(Target, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    task = models.ForeignKey(Task, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    status = models.TextField(max_length=7, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    format = models.TextField(max_length=4, choices=ReportFormat.choices)
    path = models.TextField(max_length=300, blank=True, null=True)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    @cached_property
    def parent_project(self) -> Project:
        """Get the parent project for this report.

        Traverses the hierarchical relationship to locate the associated project
        regardless of report scope level (task, target, or project).

        Returns:
            Project: The parent project object for access control and permissions.
        """
        return (self.task or self.target or self.project).parent_project

    def __str__(self) -> str:
        """Return string representation of the report.

        Returns:
            str: String in format "scope - format - user" where scope is the
                 task, target, or project associated with this report.
        """
        return " - ".join(
            [(self.task or self.target or self.project).__str__(), self.format.value, self.user.__str__()]
        )

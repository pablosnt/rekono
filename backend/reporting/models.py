"""Model of the reports that export the findings."""

from functools import cached_property

from django.db import models

from framework.models import BaseModel
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from reporting.enums import ReportFormat, ReportStatus
from targets.models import Target
from tasks.models import Task


class Report(BaseModel):
    """Report of the findings of a project, a target, or a task.

    Only one of the three scopes is set, and the report is removed together with
    the thing that it reports about.

    Attributes:
        project: Project whose findings the report includes.
        target: Target whose findings the report includes.
        task: Task whose findings the report includes.
        status: State of the generation, which starts as pending because the report
          is generated in the background.
        format: Format of the generated file.
        path: Location of the generated file, once the generation succeeds.
        user: User that requested the report.
        date: Date when the report was requested.
    """

    project = models.ForeignKey(Project, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    target = models.ForeignKey(Target, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    task = models.ForeignKey(Task, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    status = models.TextField(max_length=7, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    format = models.TextField(max_length=4, choices=ReportFormat.choices)
    path = models.TextField(max_length=300, blank=True, null=True)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    @cached_property
    def parent_project(self) -> Project:
        """The project that the report belongs to, whatever its scope is."""
        return (self.task or self.target or self.project).parent_project

    def __str__(self) -> str:
        """Return the scope of the report, with its format and the user that asked for it."""
        return " - ".join(
            [(self.task or self.target or self.project).__str__(), self.format.value, self.user.__str__()]
        )

from django.db import models
from framework.models import BaseModel
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from reporting.enums import ReportFormat, ReportStatus
from targets.models import Target
from tasks.models import Task


class Report(BaseModel):
    project = models.ForeignKey(Project, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    target = models.ForeignKey(Target, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    task = models.ForeignKey(Task, related_name="reports", on_delete=models.CASCADE, blank=True, null=True)
    status = models.TextField(max_length=7, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    format = models.TextField(max_length=4, choices=ReportFormat.choices)
    path = models.TextField(max_length=300, blank=True, null=True)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def get_project(self) -> Project:
        return (self.task or self.target or self.project).get_project()

    def __str__(self) -> str:
        return f"{(self.task or self.target or self.project).__str__()} - {self.format} - {self.user.__str__()}"

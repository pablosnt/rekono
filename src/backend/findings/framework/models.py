from typing import Any, Dict, List

from django.db import models
from executions.models import Execution
from findings.enums import TriageStatus
from framework.models import BaseInput
from security.validators.input_validator import Regex, Validator


class Finding(BaseInput):
    executions = models.ManyToManyField(
        Execution,
        related_name="%(class)s",
    )
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    triage_status = models.TextField(
        max_length=15, choices=TriageStatus.choices, default=TriageStatus.UNTRIAGED
    )
    triage_comment = models.TextField(
        max_length=300, validators=[Validator(Regex.TEXT.value, code="triage_comment")]
    )
    defect_dojo_id = models.IntegerField(blank=True, null=True)
    hacktricks_link = models.TextField(max_length=300, blank=True, null=True)
    unique_fields: List[str] = []

    class Meta:
        abstract = True

    def get_project(self) -> Any:
        return self.executions.first().task.target.project

    @classmethod
    def get_project_field(cls) -> str:
        return "executions__task__target__project"

    def defect_dojo(self) -> Dict[str, Any]:
        return {}  # pragma: no cover

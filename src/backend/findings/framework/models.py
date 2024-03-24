from typing import Any, Dict, List, Optional, Union

from django.db import models
from django.utils import timezone
from executions.models import Execution
from findings.enums import TriageStatus
from framework.models import BaseInput
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator


class FindingManager(models.Manager):

    def _update_finding_fix_data(self, finding: Any, is_fixed: bool, fixed_date: Optional[timezone.datetime] = None, fixed_by: Optional[Any] = None) -> Any:
        finding.is_fixed = is_fixed
        finding.fixed_date = fixed_date
        finding.fixed_by = fixed_by
        finding.save(update_fields=["is_fixed", "fixed_date", "fixed_by"])
        return finding
    
    def _update_findings_fix_data(self, queryset: models.QuerySet, is_fixed: bool, fixed_date: Optional[timezone.datetime] = None, fixed_by: Optional[Any] = None) -> Any:
        return queryset.update(is_fixed=is_fixed, fixed_date=fixed_date, fixed_by=fixed_by)

    def fix(self, finding: Union[Any, models.QuerySet], user: Optional[Any]) -> Any:
        args = {"is_fixed": True, "fixed_date": timezone.now(), "fixed_by": user}
        return self._update_finding_fix_data(finding, **args) if isinstance(finding, Finding) else self._update_findings_fix_data(finding, **args)
        # TODO: Fix related findings with the same user and date value

    def unfix(self, finding: Any) -> Any:
        return self._update_finding_fix_data(finding, False)
        # TODO: Unfix related findings whose fix data are the same as the current finding


class Finding(BaseInput):
    executions = models.ManyToManyField(
        Execution,
        related_name="%(class)s",
    )
    is_fixed = models.BooleanField(default=False)
    fixed_date = models.DateTimeField(blank=True, null=True)
    fixed_by = models.ForeignKey(
        AUTH_USER_MODEL, related_name="fixed_%(class)s", on_delete=models.SET_NULL, blank=True, null=True
    )
    defect_dojo_id = models.IntegerField(blank=True, null=True)
    hacktricks_link = models.TextField(max_length=300, blank=True, null=True)
    objects = FindingManager()
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


class TriageFinding(Finding):
    triage_status = models.TextField(
        max_length=15, choices=TriageStatus.choices, default=TriageStatus.UNTRIAGED
    )
    triage_comment = models.TextField(
        max_length=300,
        validators=[Validator(Regex.TEXT.value, code="triage_comment")],
        blank=True,
        null=True,
    )
    triage_date = models.DateTimeField(blank=True, null=True)
    triage_by = models.ForeignKey(
        AUTH_USER_MODEL, related_name="triaged_%(class)s", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        abstract = True

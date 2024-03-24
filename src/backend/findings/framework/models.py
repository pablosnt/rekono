import uuid
from typing import Any, Dict, List, Optional, Union

from django.db import models
from django.utils import timezone
from executions.models import Execution
from findings.enums import TriageStatus
from framework.models import BaseInput
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator

from backend.input_types.models import InputType


class FindingManager(models.Manager):
    def _get_related_findings(
        self, finding: Any, filter: Optional[Dict[str, Any]]
    ) -> List[Any]:
        related_findings: List[Any] = []
        input_type = InputType.objects.filter(
            model=f"findings.{(finding if isinstance(finding, Finding) else finding.first()).__class__.__name__.lower()}"
        )
        for related_input_type in input_type.get_related_input_types():
            finding_type = related_input_type.get_model_class()
            new_related_findings = (
                finding_type.objects.all()
                if not filter
                else finding_type.objects.filter(**filter).all()
            )
            if new_related_findings:
                related_findings.extend(new_related_findings)
                for new_related_finding in new_related_findings:
                    related_findings.extend(
                        self._get_related_findings(new_related_finding)
                    )
        return related_findings

    def _update_finding_fix_data(
        self,
        finding: Any,
        is_fixed: bool,
        auto_fixed: Optional[bool] = False,
        fixed_date: Optional[timezone.datetime] = None,
        fixed_by: Optional[Any] = None,
    ) -> Any:
        finding.is_fixed = is_fixed
        finding.auto_fixed = auto_fixed
        finding.fixed_date = fixed_date
        finding.fixed_by = fixed_by
        finding.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        return finding

    def _update_findings_fix_data(
        self,
        queryset: models.QuerySet,
        is_fixed: bool,
        auto_fixed: bool,
        fixed_date: Optional[timezone.datetime] = None,
        fixed_by: Optional[Any] = None,
    ) -> Any:
        return queryset.update(
            is_fixed=is_fixed,
            auto_fixed=auto_fixed,
            fixed_date=fixed_date,
            fixed_by=fixed_by,
        )

    def fix(
        self, findings: Union[Any, models.QuerySet], fixed_by: Optional[Any]
    ) -> Union[Any, models.QuerySet]:
        if not findings:
            return findings
        args = {
            "is_fixed": True,
            "auto_fixed": fixed_by is None,
            "fixed_date": timezone.now(),
            "fixed_by": fixed_by,
        }
        updated_finding = (
            self._update_finding_fix_data(findings, **args)
            if isinstance(findings, Finding)
            else self._update_findings_fix_data(findings, **args)
        )
        args["auto_fixed"] = True
        for finding in [findings] if isinstance(findings, Finding) else findings:
            for related_finding in self._get_related_findings(finding):
                self._update_finding_fix_data(related_finding, **args)
        return updated_finding

    def unfix(self, finding: Any, fixed_by: Optional[Any]) -> Any:
        updated_finding = self._update_finding_fix_data(finding, False)
        if fixed_by:
            for related_finding in self._get_related_findings(
                finding, {"is_fixed": True, "auto_fixed": True, "fixed_by": fixed_by}
            ):
                self._update_finding_fix_data(related_finding, False)
        return updated_finding


class Finding(BaseInput):
    executions = models.ManyToManyField(
        Execution,
        related_name="%(class)s",
    )
    is_fixed = models.BooleanField(default=False)
    auto_fixed = models.BooleanField(default=False)
    fixed_date = models.DateTimeField(blank=True, null=True)
    fixed_by = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="fixed_%(class)s",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
        AUTH_USER_MODEL,
        related_name="triaged_%(class)s",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

"""Base models for the findings framework.

This module provides the foundational model classes for the findings system,
including the base Finding and TriageFinding models that all specific
finding types inherit from. It also includes the FindingManager for
handling finding-specific operations like fixing and removing fixes.
"""

from functools import cached_property
from typing import Any, Callable

from django.db.models import (
    SET_NULL,
    BooleanField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    Manager,
    ManyToManyField,
    QuerySet,
    TextField,
)
from django.utils import timezone

from executions.models import Execution
from findings.enums import TriageStatus
from framework.models import BaseInput
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class FindingManager(Manager):
    """Manager for Finding models with specialized operations.

    Provides methods for handling finding-specific operations like
    fixing findings, removing fixes, and managing related findings.
    """

    def _get_related_findings(self, finding: "Finding", **kwargs: Any) -> list[Any]:
        """Get all findings related to a given finding.

        Recursively traverses the relationship tree to find all findings
        that are related to the given finding through input type
        relationships.

        Args:
            finding: The finding to find related findings for.
            **kwargs: Additional filter criteria.

        Returns:
            List of related findings.
        """
        related_findings = []
        for input_type in finding.input_type.related_input_types:
            new_related_findings = input_type.model_class.objects.filter(
                **{**kwargs, input_type.name.lower(): finding}
            ).all()
            if new_related_findings:
                related_findings.extend(new_related_findings)
                for new_related_finding in new_related_findings:
                    related_findings.extend(self._get_related_findings(new_related_finding, **kwargs))
        return related_findings

    def fix(self, findings: Any | QuerySet, fixed_by: Any | None = None) -> Any | QuerySet:
        """Mark findings as fixed.

        Marks findings as fixed and automatically fixes related findings
        that were auto-fixed when the original finding was fixed.

        Args:
            findings: Single finding or queryset of findings to fix.
            fixed_by: User who fixed the findings (None for auto-fix).

        Returns:
            The fixed finding(s).
        """
        if not findings:
            return findings
        if isinstance(findings, Finding):
            findings.is_fixed = True
            findings.auto_fixed = fixed_by is None
            findings.fixed_date = timezone.now()
            findings.fixed_by = fixed_by
            findings.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        else:
            findings = findings.update(
                is_fixed=True,
                auto_fixed=fixed_by is None,
                fixed_date=timezone.now(),
                fixed_by=fixed_by,
            )
        # Fix related findings
        for finding in [findings] if isinstance(findings, Finding) else findings:
            for related_finding in self._get_related_findings(finding):
                related_finding.is_fixed = True
                related_finding.auto_fixed = True
                related_finding.fixed_date = timezone.now()
                related_finding.fixed_by = fixed_by
                related_finding.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        return findings

    def remove_fix(self, finding: Any, fixed_by: Any | None = None) -> Any:
        """Remove the fixed status from a finding.

        Removes the fixed status from a finding and handles related
        findings that were auto-fixed when the original finding was fixed.

        Args:
            finding: The finding to remove fix from.
            fixed_by: User who removed the fix (None for auto-remove).

        Returns:
            The finding with fix removed.
        """
        if fixed_by:
            # Remove auto-fix from related findings that were auto-fixed
            for auto_fixed_and_related_finding in self._get_related_findings(
                finding, {"is_fixed": True, "auto_fixed": True, "fixed_by": finding.fixed_by}
            ):
                auto_fixed_and_related_finding.is_fixed = False
                auto_fixed_and_related_finding.auto_fixed = False
                auto_fixed_and_related_finding.fixed_date = None
                auto_fixed_and_related_finding.fixed_by = None
                auto_fixed_and_related_finding.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        finding.is_fixed = False
        finding.auto_fixed = False
        finding.fixed_date = None
        finding.fixed_by = None
        finding.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        return finding


class Finding(BaseInput):
    """Base model for all security findings.

    Abstract base class that provides common functionality for all
    finding types, including fixing status, DefectDojo integration,
    and relationship management.

    Attributes:
        executions: Many-to-many relationship with executions.
        is_fixed: Whether the finding has been marked as fixed.
        auto_fixed: Whether the finding was automatically fixed.
        fixed_date: When the finding was fixed.
        fixed_by: User who fixed the finding.
        defectdojo_id: ID in DefectDojo platform.
        hacktricks_link: Link to HackTricks documentation.
    """

    executions = ManyToManyField(Execution, related_name="%(class)s")
    is_fixed = BooleanField(default=False)
    auto_fixed = BooleanField(default=False)
    fixed_date = DateTimeField(blank=True, null=True)
    fixed_by = ForeignKey(AUTH_USER_MODEL, related_name="fixed_%(class)s", on_delete=SET_NULL, blank=True, null=True)
    defectdojo_id = IntegerField(blank=True, null=True)
    hacktricks_link = TextField(max_length=300, blank=True, null=True)

    objects = FindingManager()
    unique_fields: list[str] = []
    _project_field = "executions__task__target__project"
    _defectdojo_finding_mapping: dict[str, Any | Callable] = {}
    _defectdojo_endpoint_mapping: dict[str, Any | Callable] = {}

    class Meta:
        abstract = True

    @cached_property
    def parent_project(self) -> Project:
        """Get the parent project for this finding.

        Returns:
            The project that this finding belongs to.
        """
        return self.executions.first().task.target.project

    def _apply_defectdojo_mapping(self, mapping: dict[str, Any], target: Target | None = None) -> dict[str, Any]:
        """Apply DefectDojo mapping to the finding.

        Parses the fiding data, according to the mapping dictionary.

        Args:
            mapping: The mapping dictionary to apply.
            target: Optional target for context.

        Returns:
            Processed mapping dictionary.
        """
        data = {}
        for key, value in mapping.items():
            if callable(value):
                data[key] = value(self, target) if target else value(self)
            else:
                if isinstance(value, str) and hasattr(self, value):
                    data[key] = getattr(self, value)
                else:
                    data[key] = value
        return data

    def defectdojo_finding(self) -> dict[str, Any]:
        """Generate DefectDojo finding data.

        Returns:
            Dictionary with DefectDojo finding data.
        """
        return self._apply_defectdojo_mapping(self._defectdojo_finding_mapping)

    def defectdojo_endpoint(self, target: Target) -> dict[str, Any]:
        """Generate DefectDojo endpoint data.

        Args:
            target: The target for the endpoint.

        Returns:
            Dictionary with DefectDojo endpoint data.
        """
        return self._apply_defectdojo_mapping(self._defectdojo_endpoint_mapping, target)

    def __str__(self) -> str:
        """String representation of the finding.

        Returns:
            String representation of the finding.
        """
        return " - ".join([field.__str__() for field in self.unique_fields if field])


class TriageFinding(Finding):
    """Base model for findings that support triage.

    Extends the base Finding model to add triage functionality,
    allowing findings to be marked as false positives, true positives,
    or won't fix with comments and tracking.

    Attributes:
        triage_status: Current triage status of the finding.
        triage_comment: Comment explaining the triage decision.
        triage_date: When the finding was triaged.
        triage_by: User who performed the triage.
    """

    triage_status = TextField(max_length=15, choices=TriageStatus.choices, default=TriageStatus.UNTRIAGED)
    triage_comment = TextField(
        max_length=300, validators=[Validator(Regex.TEXT.value, code="triage_comment")], blank=True, null=True
    )
    triage_date = DateTimeField(blank=True, null=True)
    triage_by = ForeignKey(AUTH_USER_MODEL, related_name="triaged_%(class)s", on_delete=SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True

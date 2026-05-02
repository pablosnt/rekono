"""Base model classes for findings framework architecture.

Provides foundational model classes including Finding and TriageFinding
that all specific finding types inherit from, along with FindingManager
for specialized operations like fixing and relationship management.
"""

from functools import cached_property
from typing import Any, Callable

from django.db.models import (
    SET_NULL,
    BooleanField,
    DateTimeField,
    ForeignKey,
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


class FindingManager(Manager):
    """Custom manager for Finding models with specialized operations.

    Extends Django's Manager to provide finding-specific operations including
    fixing/unfixing findings, managing related finding relationships, and
    handling automatic finding lifecycle management.
    """

    def _get_related_findings(self, finding: "Finding", **kwargs: Any) -> list[Any]:
        """Get all findings related to a given finding through input relationships.

        Recursively traverses the relationship tree to identify all findings
        connected to the specified finding through input type relationships
        for automatic fixing propagation.

        Args:
            finding (Finding): Source finding to find relationships for.
            **kwargs (Any): Additional filter criteria for related findings.

        Returns:
            list[Any]: List of related findings in the relationship tree.
        """
        related_findings = []
        for input_type in finding.input_type.children_input_types:
            new_related_findings = input_type.model_class.objects.filter(
                **{**kwargs, finding.input_type.name.lower(): finding}
            ).all()
            if new_related_findings:
                related_findings.extend(new_related_findings)
                for new_related_finding in new_related_findings:
                    related_findings.extend(self._get_related_findings(new_related_finding, **kwargs))
        return related_findings

    def fix(self, findings: Any | QuerySet, fixed_by: Any | None = None) -> Any | QuerySet:
        """Mark findings as fixed with automatic relationship handling.

        Marks findings as fixed and automatically propagates the fix status
        to related findings with proper tracking of manual vs automatic fixes.

        Args:
            findings (Any | QuerySet): Single finding or queryset to fix.
            fixed_by (Any | None): User who fixed the findings, None for auto-fix.

        Returns:
            Any | QuerySet: The fixed finding(s) with updated status.
        """
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
        """Remove fixed status from finding with relationship cleanup.

        Removes the fixed status from a finding and handles cleanup of
        related findings that were automatically fixed as a consequence.

        Args:
            finding (Any): Finding to remove fix status from.
            fixed_by (Any | None): User removing the fix, None for auto-remove.

        Returns:
            Any: Finding instance with fix status removed.
        """
        if fixed_by:
            # Remove auto-fix from related findings that were auto-fixed
            for auto_fixed_and_related_finding in self._get_related_findings(
                finding, is_fixed=True, auto_fixed=True, fixed_by=finding.fixed_by
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

    def create_finding(self, finding_type: type[BaseInput], execution: Execution, **fields: Any) -> Any:
        """Create or update a finding with duplicate prevention and user input handling.

        Creates a new finding or updates an existing one based on unique fields and target.

        Args:
            finding_type (type[BaseInput]): The finding class to create
            execution (Execution): The execution context for this finding
            **fields (Any): Field values for the finding

        Returns:
            Any: The created or updated finding instance
        """
        # Check if a finding with the same unique characteristics already exists for this target
        # This prevents duplicate findings while allowing updates to existing ones
        unique_finding = finding_type.objects.filter(
            **{
                **{f: fields.get(f) for f in finding_type.unique_fields},
                "executions__task__target": execution.task.target,
            }
        )
        if unique_finding.exists():
            # Update existing finding with new field values
            finding = unique_finding.first()
            for field, value in fields.items():
                if finding.created_from_user_input is False and field == "created_from_user_input":
                    continue
                setattr(finding, field, value)
            finding.save(update_fields=fields.keys())
        else:
            # Create new finding if no duplicate exists
            finding = finding_type.objects.create(**fields)
        # Associate this finding with the current execution for tracking
        finding.executions.add(execution)
        return finding


class Finding(BaseInput):
    """Abstract base model for all security findings.

    Provides common functionality for all finding types including fixing status
    tracking, DefectDojo integration, relationship management, and automatic
    lifecycle operations with execution history.

    Attributes:
        executions (ManyToManyField): Related executions that discovered this finding.
        is_fixed (BooleanField): Whether finding has been marked as fixed (default: False).
        auto_fixed (BooleanField): Whether finding was automatically fixed (default: False).
        fixed_date (DateTimeField): Timestamp when finding was fixed (optional).
        fixed_by (ForeignKey): User who fixed the finding (optional).
        hacktricks_link (TextField): HackTricks documentation link (optional, max 300 chars).
        created_from_user_input (BooleanField): Whether finding was created from user input (default: False).
    """

    executions = ManyToManyField(Execution, related_name="%(class)s")
    is_fixed = BooleanField(default=False)
    auto_fixed = BooleanField(default=False)
    fixed_date = DateTimeField(blank=True, null=True)
    fixed_by = ForeignKey(AUTH_USER_MODEL, related_name="fixed_%(class)s", on_delete=SET_NULL, blank=True, null=True)
    hacktricks_link = TextField(max_length=300, blank=True, null=True)
    created_from_user_input = BooleanField(default=False)

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

        Retrieves the project context through the execution relationship
        for access control and organizational purposes.

        Returns:
            Project: Parent project containing this finding.
        """
        return self.executions.first().task.target.project

    def _apply_defectdojo_mapping(self, mapping: dict[str, Any]) -> dict[str, Any]:
        """Apply DefectDojo field mapping to finding data.

        Processes finding fields according to the mapping configuration. Callable
        values are invoked with the finding instance; string values are resolved
        as attribute names; all other values are used as-is.

        Args:
            mapping (dict[str, Any]): Field mapping configuration dictionary.

        Returns:
            dict[str, Any]: Processed data dictionary for DefectDojo integration.
        """
        data = {}
        for key, value in mapping.items():
            if callable(value):
                data[key] = value(self)
            else:
                if isinstance(value, str) and hasattr(self, value):
                    data[key] = getattr(self, value)
                else:
                    data[key] = value
        return data

    def defectdojo_finding(self) -> dict[str, Any]:
        """Generate DefectDojo finding data for platform integration.

        Creates formatted finding data suitable for DefectDojo platform
        integration using the configured finding mapping.

        Returns:
            dict[str, Any]: DefectDojo-formatted finding data.
        """
        default_mapping = {"active": lambda instance: not instance.is_fixed, "is_mitigated": "is_fixed"}
        if hasattr(self, "triage_status"):
            default_mapping.update(
                {
                    "active": lambda instance: (
                        not instance.is_fixed
                        and instance.triage_status in [TriageStatus.UNTRIAGED, TriageStatus.TRUE_POSITIVE]
                    ),
                    "verified": lambda instance: instance.triage_status == TriageStatus.TRUE_POSITIVE,
                    "false_p": lambda instance: instance.triage_status == TriageStatus.FALSE_POSITIVE,
                    "risk_accepted": lambda instance: instance.triage_status == TriageStatus.WONT_FIX,
                }
            )
        return self._apply_defectdojo_mapping({**self._defectdojo_finding_mapping, **default_mapping})

    def defectdojo_endpoint(self) -> dict[str, Any]:
        """Generate DefectDojo endpoint data for platform integration.

        Creates formatted endpoint data suitable for DefectDojo platform
        integration using the configured endpoint mapping.

        Returns:
            dict[str, Any]: DefectDojo-formatted endpoint data.
        """
        return self._apply_defectdojo_mapping(self._defectdojo_endpoint_mapping)

    def __str__(self) -> str:
        """String representation of the finding.

        Generates human-readable string using unique field values
        for finding identification and display purposes.

        Returns:
            str: Formatted string representation of the finding.
        """
        return " - ".join([getattr(self, field).__str__() for field in self.unique_fields if getattr(self, field)])


class TriageFinding(Finding):
    """Abstract base model for findings requiring triage workflow.

    Extends Finding to add triage functionality enabling findings to be
    classified as false positives, true positives, or won't fix with
    detailed tracking and audit trails.

    Attributes:
        triage_status (TextField): Current triage status from TriageStatus enum (default: UNTRIAGED, max 15 chars).
        triage_comment (TextField): Comment explaining triage decision (optional, max 300 chars).
        triage_date (DateTimeField): Timestamp when finding was triaged (optional).
        triage_by (ForeignKey): User who performed the triage operation (optional).
    """

    triage_status = TextField(max_length=15, choices=TriageStatus.choices, default=TriageStatus.UNTRIAGED)
    triage_comment = TextField(
        max_length=300, validators=[Validator(Regex.TEXT, code="triage_comment")], blank=True, null=True
    )
    triage_date = DateTimeField(blank=True, null=True)
    triage_by = ForeignKey(AUTH_USER_MODEL, related_name="triaged_%(class)s", on_delete=SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True

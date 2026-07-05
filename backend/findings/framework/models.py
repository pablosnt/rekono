"""Base model classes for findings framework architecture.

Provides foundational model classes including Finding and TriageFinding
that all specific finding types inherit from, along with FindingManager
for specialized operations like fixing and relationship management.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable

from django.db.models import (
    SET_NULL,
    BooleanField,
    DateTimeField,
    ForeignKey,
    Manager,
    ManyToManyField,
    Q,
    QuerySet,
    TextField,
)
from django.utils import timezone

from executions.models import Execution
from findings.enums import AutoFixedReason, TriageStatus
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
        # A fix without a user is an automatic one triggered because the finding is no longer
        # detected; a user-driven fix is manual and keeps the auto-fix reason empty
        auto_fixed_reason = AutoFixedReason.NO_LONGER_DETECTED if fixed_by is None else None
        if isinstance(findings, Finding):
            findings.is_fixed = True
            findings.auto_fixed = auto_fixed_reason
            findings.fixed_date = timezone.now()
            findings.fixed_by = fixed_by
            findings.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        else:
            findings.update(
                is_fixed=True,
                auto_fixed=auto_fixed_reason,
                fixed_date=timezone.now(),
                fixed_by=fixed_by,
            )
        # Fix related findings
        for finding in [findings] if isinstance(findings, Finding) else findings:
            for related_finding in self._get_related_findings(finding):
                related_finding.is_fixed = True
                related_finding.auto_fixed = AutoFixedReason.PARENT_FIXED
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
                finding, is_fixed=True, auto_fixed__isnull=False, fixed_by=finding.fixed_by
            ):
                auto_fixed_and_related_finding.is_fixed = False
                auto_fixed_and_related_finding.auto_fixed = None
                auto_fixed_and_related_finding.fixed_date = None
                auto_fixed_and_related_finding.fixed_by = None
                auto_fixed_and_related_finding.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        finding.is_fixed = False
        finding.auto_fixed = None
        finding.fixed_date = None
        finding.fixed_by = None
        finding.save(update_fields=["is_fixed", "auto_fixed", "fixed_date", "fixed_by"])
        return finding

    def create_finding(self, execution: Execution, **fields: Any) -> Any:
        """Create or update a finding with duplicate prevention.

        Reuses the existing finding returned by ``self.model._find_duplicate`` or creates a new one.
        A detected finding completes the one it matched (``_merge``); a user-provided finding attaches
        without modifying it. The finding is always associated with the current execution.

        Args:
            execution (Execution): The execution context for this finding.
            **fields (Any): Field values for the finding.

        Returns:
            Any: The created or updated finding instance.
        """
        is_user_input = bool(fields.get("created_from_user_input"))
        finding = self.model._find_duplicate(execution, fields)
        if finding:
            if not is_user_input:
                self._merge(finding, fields)
        else:
            finding = self.create(**fields)
        finding.executions.add(execution)
        return finding

    def _merge(self, finding: Any, fields: dict[str, Any]) -> None:
        """Complete an existing finding with the incoming detected values.

        Fills blank fields without overwriting known ones, skipping root fields. Then applies the
        directional root rule: if the incoming finding provides a deeper root (``_root_findings`` are
        declared deep-first) that the existing finding lacks, upgrade by adopting the incoming deep
        root and clearing the shallower one to keep a single parent link; otherwise the existing
        (richer or equal) root is preserved untouched.

        Args:
            finding (Any): The existing finding to complete.
            fields (dict[str, Any]): Field values from the incoming finding.
        """
        updated_fields = []
        for field, value in fields.items():
            # Never overwrite an already known value with a blank one
            if field in self.model._root_findings or (
                value in (None, "") and getattr(finding, field) not in (None, "")
            ):
                continue
            setattr(finding, field, value)
            updated_fields.append(field)
        if len(self.model._root_findings) > 1:
            for index, root_finding in enumerate(self.model._root_findings):
                if getattr(finding, root_finding) is not None:
                    break
                elif fields.get(root_finding) is not None:
                    setattr(finding, root_finding, fields.get(root_finding))
                    updated_fields.append(root_finding)
                    for pending_root_finding in self.model._root_findings[index + 1 :]:
                        setattr(finding, pending_root_finding, None)
                        updated_fields.append(pending_root_finding)
                    break
        if updated_fields:
            finding.save(update_fields=updated_fields)


class Finding(BaseInput):
    """Abstract base model for all security findings.

    Provides common functionality for all finding types including fixing status
    tracking, DefectDojo integration, relationship management, and automatic
    lifecycle operations with execution history.

    Attributes:
        executions (ManyToManyField): Related executions that discovered this finding.
        is_fixed (BooleanField): Whether finding has been marked as fixed (default: False).
        auto_fixed (TextField): Reason for automatic fixing (None if manually fixed, values from AutoFixedReason).
        fixed_date (DateTimeField): Timestamp when finding was fixed (optional).
        fixed_by (ForeignKey): User who fixed the finding (optional).
        created_from_user_input (BooleanField): Whether finding was created from user input (default: False).
    """

    executions = ManyToManyField(Execution, related_name="%(class)s")
    is_fixed = BooleanField(default=False)
    auto_fixed = TextField(max_length=50, blank=True, null=True, choices=AutoFixedReason.choices)
    fixed_date = DateTimeField(blank=True, null=True)
    fixed_by = ForeignKey(AUTH_USER_MODEL, related_name="fixed_%(class)s", on_delete=SET_NULL, blank=True, null=True)
    created_from_user_input = BooleanField(default=False)

    objects = FindingManager()
    _unique_fields: list["Finding.UniqueField"] = []
    # Fields linking this finding to its parent finding(s), ordered by priority for deduplication:
    # the deepest (most specific) root comes first, so a match can be upgraded to its deepest known
    # root while the shallower roots are cleared to keep a single parent link (see FindingManager._merge)
    _root_findings: tuple[str, ...] = ()
    _project_field = "executions__task__target__project"
    _defectdojo_finding_mapping: dict[str, Any | Callable] = {}
    _defectdojo_endpoint_mapping: dict[str, Any | Callable] = {}

    class Meta:
        abstract = True

    @dataclass
    class UniqueField:
        """Declarative configuration of a field used to identify duplicate findings.

        Attributes:
            field (str): Model field name to match on.
            match_null_and_empty (bool): Whether a blank value (null or, for char/text fields, empty)
                is treated as compatible with anything on this field: an existing finding blank on it
                matches an incoming real value, and an incoming blank value drops it from the match.
        """

        field: str
        match_null_and_empty: bool = False

    @classmethod
    def _find_duplicate(cls, execution: Execution, fields: dict[str, Any]) -> "Finding | None":
        """Find an existing finding that duplicates the incoming one, or None.

        Matches on every ``_unique_fields`` value for the same target. A ``match_null_and_empty``
        field is dropped when the incoming value is blank, and otherwise also matches existing blanks
        so a partial finding can be completed. Complex finding types override this method.

        Args:
            execution (Execution): The execution context for this finding.
            fields (dict[str, Any]): Field values the finding is being created/matched with.

        Returns:
            Finding | None: The matched finding, or None if there is no duplicate.
        """
        query = Q(executions__task__target=execution.task.target)
        for unique_field in cls._unique_fields:
            field_query = cls._get_deduplication_field_query(unique_field, fields.get(unique_field.field))
            if field_query is not None:
                query &= field_query
        return cls.objects.filter(query).order_by("id").first()

    @classmethod
    def _get_deduplication_field_query(cls, unique_field: UniqueField, new_value: Any) -> Q | None:
        """Build the deduplication query fragment for a single unique field.

        Returns None when the field should not constrain the match: a ``match_null_and_empty`` field
        is dropped entirely when the incoming value is blank. Otherwise it matches the value, and for
        a ``match_null_and_empty`` field it also matches existing blanks (null, and empty string for
        char/text fields) so a partial finding can still be completed by a more detailed one.

        Args:
            unique_field (UniqueField): The unique field configuration to build the fragment for.
            new_value (Any): The incoming value for that field.

        Returns:
            Q | None: Query fragment matching this field, or None if it should not constrain the match.
        """
        if unique_field.match_null_and_empty and new_value in (None, ""):
            return
        field_query = Q(**{unique_field.field: new_value})
        if unique_field.match_null_and_empty:
            field_query |= Q(**{f"{unique_field.field}__isnull": True})
            if cls._meta.get_field(unique_field.field).get_internal_type() in ["CharField", "TextField"]:
                field_query |= Q(**{unique_field.field: ""})
        return field_query

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
        return " - ".join(
            [
                getattr(self, unique_field.field).__str__()
                for unique_field in self.__class__._unique_fields
                if getattr(self, unique_field.field)
            ]
        )


class HacktricksFinding(Finding):
    """Abstract base model for findings enriched with HackTricks documentation.

    Extends Finding to add HackTricks integration support. Only finding types
    whose characteristics can be mapped to a HackTricks penetration testing
    guide (hosts, ports, and technologies) should inherit from this class.

    Attributes:
        hacktricks_link (TextField): HackTricks documentation link (optional, max 300 chars).
    """

    hacktricks_link = TextField(max_length=300, blank=True, null=True)

    class Meta:
        abstract = True


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

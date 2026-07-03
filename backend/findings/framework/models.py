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

    def _resolve_unique_value(self, lookups: list[str], fields: dict[str, Any]) -> Any:
        """Resolve the value to match on when a user-provided finding is involved.

        A user-provided finding only carries partial information, so a field it's matched on
        might not be set directly, only reachable through a related field instead. This method
        only runs for fields with ``user_input_lookups``, and tries each declared path in order,
        returning the first one with a value. For example, a Vulnerability normally has its
        "port" set directly, but a finding built from a technology alone has no "port" key at
        all; ``user_input_lookups = ["port", "technology__port"]`` lets this method fall back to
        reading ``.port`` off ``fields["technology"]`` in that case.

        Args:
            lookups (list[str]): Paths to try, in order, as declared on ``user_input_lookups``.
            fields (dict[str, Any]): Field values the finding is being created/matched with.

        Returns:
            Any: The first resolved, non-empty value, or None if no path resolves.
        """
        for lookup in lookups:
            segments = lookup.split("__")
            value = fields.get(segments[0])
            for segment in segments[1:]:
                if value is None:
                    break
                value = getattr(value, segment)
            if value:
                return value
        return None

    def _unique_findings_query(
        self,
        execution: Execution,
        fields: dict[str, Any],
        skip_user_input_ignorable: bool,
        use_user_input_lookups: bool,
    ) -> Q:
        """Build the query matching findings sharing the same unique characteristics.

        Args:
            execution (Execution): The execution context for this finding.
            fields (dict[str, Any]): Field values the finding is being created/matched with.
            skip_user_input_ignorable (bool): Whether to drop fields marked ``ignore_for_user_input`` from
                the query, because either side of the match is user-provided.
            use_user_input_lookups (bool): Whether to use each field's ``user_input_lookups``.

        Returns:
            Q: Query matching findings for the same target sharing the finding's unique fields.
        """
        query = Q(executions__task__target=execution.task.target)
        for unique_field in self.model._unique_fields:
            if not unique_field.active(fields) or (skip_user_input_ignorable and unique_field.ignore_for_user_input):
                continue
            value = fields.get(unique_field.field)
            lookups = [unique_field.field]
            if use_user_input_lookups:
                lookups = unique_field.user_input_lookups or lookups
                if len(lookups) > 1:
                    value = self._resolve_unique_value(lookups, fields)
            if unique_field.match_null_and_empty and value in (None, ""):
                continue
            field_query = Q()
            for field in lookups:
                field_query |= Q(**{field: value})
                if unique_field.match_null_and_empty:
                    field_query |= Q(**{f"{field}__isnull": True})
                    # Always check the primary field's type, even for a lookup fallback path,
                    # since both are expected to point to fields of the same type
                    if self.model._meta.get_field(unique_field.field).get_internal_type() in ["CharField", "TextField"]:
                        field_query |= Q(**{field: ""})
            query &= field_query
        return query

    def create_finding(self, execution: Execution, **fields: Any) -> Any:
        """Create or update a finding with duplicate prevention and user input handling.

        Creates a new finding for the current target, or reuses an existing one that already
        represents it. A detected finding (created from parser output) matches strictly on its
        own unique fields, but also checks for a looser-matching user-provided finding it can
        complete. A user-provided finding matches loosely, ignoring fields it structurally can't
        supply and following its declared ``user_input_lookups`` fallbacks, and always attaches
        to the finding it matches without overwriting it.

        Args:
            execution (Execution): The execution context for this finding
            **fields (Any): Field values for the finding

        Returns:
            Any: The created or updated finding instance
        """
        is_user_input = bool(fields.get("created_from_user_input"))
        if is_user_input:
            query = self._unique_findings_query(
                execution, fields, skip_user_input_ignorable=True, use_user_input_lookups=True
            )
        else:
            # A detected finding can duplicate either another detected finding, or a
            # user-provided one it should complete instead of creating a new duplicate
            query = self._unique_findings_query(
                execution, fields, skip_user_input_ignorable=False, use_user_input_lookups=False
            ) | (
                Q(created_from_user_input=True)
                & self._unique_findings_query(
                    execution, fields, skip_user_input_ignorable=True, use_user_input_lookups=True
                )
            )
        unique_finding = self.model.objects.filter(query)
        if unique_finding.exists():
            finding = unique_finding.first()
            if not is_user_input:
                # Fill in blanks left by the matched finding, but never overwrite an already
                # known value with a blank one. A blank value is None or an empty string, not
                # any falsy value, so meaningful flags like created_from_user_input=False are
                # still applied
                for field, value in fields.items():
                    if value in (None, "") and getattr(finding, field):
                        continue
                    setattr(finding, field, value)
                finding.save(update_fields=fields.keys())
        else:
            # Create new finding if no duplicate exists
            finding = self.model.objects.create(**fields)
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
            match_null_and_empty (bool): Whether a blank value (null or, for char/text fields,
                empty) is treated as compatible with anything on this field. An existing finding
                still blank on this field matches an incoming real value, so it can be completed
                by a later, more detailed finding. Conversely, when the incoming value itself is
                blank, this field is dropped from the match entirely rather than requiring the
                existing finding to also be blank, so fields a finding leaves unset (e.g. a
                user-provided port has no protocol) don't block it from matching an already
                fully-detected finding.
            ignore_for_user_input (bool): Whether to drop this field from the query whenever a
                user-provided finding is involved on either side of the match, because a
                user-provided finding structurally never supplies it (e.g. a vulnerability added
                from a CVE parameter never carries a technology).
            user_input_lookups (list[str] | None): Extra query paths OR'd in alongside ``field``,
                used only while a user-provided finding searches outward for a match. A
                user-provided finding is temporary and partial, so it is forced to attach to a
                detected finding reachable through an alternate relation (e.g. a vulnerability
                tied directly to a port, matching one a tool already tied to a technology found
                on that same port).
            active (Callable[[dict[str, Any]], bool]): Whether this field currently participates
                in the match, given the incoming field values. Defaults to always active. Lets a
                field yield to a more specific one without a per-model method override (e.g. a
                vulnerability name is dropped from matching once its CVE is known).
        """

        field: str
        match_null_and_empty: bool = False
        ignore_for_user_input: bool = False
        user_input_lookups: list[str] | None = None
        active: Callable[[dict[str, Any]], bool] = lambda fields: True

    _unique_fields: list["Finding.UniqueField"] = []

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

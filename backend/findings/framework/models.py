"""Base models of the findings, and the manager that creates and fixes them.

The manager implements the deduplication that keeps one finding per discovery, no
matter how many executions report it, and the propagation of the fixes through the
findings that were discovered inside another one.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable

from django.db import transaction
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
from findings.enums import AutoFixedReason, Severity, TriageStatus
from framework.models import BaseInput
from projects.models import Project
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class FindingManager(Manager):
    """Manager that creates the findings and manages their fixed status."""

    def _get_related_findings(self, finding: "Finding", **kwargs: Any) -> list[Any]:
        """Get all the findings discovered inside a finding, at any depth.

        Args:
            finding: Finding whose children are searched, like a host whose ports
              and paths are returned.
            **kwargs: Extra conditions that the returned findings must match.

        Returns:
            Every descendant finding, flattened into a single list.
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
        """Mark findings as fixed, and the ones discovered inside them too.

        Args:
            findings: One finding or a queryset with several of them.
            fixed_by: User that fixed them, or None when Rekono fixes them because
              they aren't detected anymore.

        Returns:
            The same finding or queryset that was given, already updated. The
            findings discovered inside them are fixed too, but they aren't part of
            the result.
        """
        # A fix without a user is automatic, triggered because the finding is no longer detected
        # A user-driven fix is manual and keeps the auto-fix reason empty
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
        """Mark a finding as not fixed anymore.

        Args:
            finding: Finding that isn't fixed anymore.
            fixed_by: User performing a manual removal, which also clears the
              auto-fix from related findings. None for an automatic removal,
              which skips that cascade.

        Returns:
            The same finding that was given, already updated.
        """
        if fixed_by:
            # Related findings were auto-fixed by the same user who originally fixed this one, so
            # match on finding.fixed_by (the original fixer) rather than the fixed_by argument
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

    @transaction.atomic()
    def create_finding(self, execution: Execution, **fields: Any) -> Any:
        """Create a finding, or reuse the one that was already discovered.

        Reuses the existing finding returned by ``self.model._find_duplicate`` or creates a new one.
        A detected finding completes the one it matched (``_merge``); a user-provided finding attaches
        without modifying it. The finding is always associated with the current execution. Runs inside
        a transaction that locks the task's target row, so two concurrent executions on the same target
        cannot create the same finding at once.

        Args:
            execution: Execution that discovered the finding.
            **fields: Values of the finding fields.

        Returns:
            The finding, which is related to this execution and to all the previous
            ones that discovered it too.
        """
        is_user_input = bool(fields.get("created_from_user_input"))
        # Lock the task's target row during the findings creation
        # This avoids duplication errors if two concurrent executions
        # try to create the same findings at the same time
        Target.objects.select_for_update().get(pk=execution.task.target_id)
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
        root; a shallower root is kept only when the incoming finding also asserts it (keeping the most
        informative link) and cleared otherwise. When the existing finding already holds an equal or
        deeper root it is preserved untouched.

        Args:
            finding: Finding that was already discovered.
            fields: Values reported by the finding that matched it.
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
                    # Adopt each shallower root from the incoming finding, keeping it when asserted
                    # and clearing it otherwise so the deeper root just adopted stays the single link
                    for pending_root_finding in self.model._root_findings[index + 1 :]:
                        setattr(finding, pending_root_finding, fields.get(pending_root_finding))
                        updated_fields.append(pending_root_finding)
                    break
        if updated_fields:
            finding.save(update_fields=updated_fields)


class Finding(BaseInput):
    """Base model of everything that the tools discover about a target.

    Findings are also inputs of the executions, so what one tool discovers can be
    used by the next one.

    Attributes:
        executions: Executions that discovered this finding, which are several when
          it keeps being detected.
        is_fixed: Whether the finding isn't there anymore.
        auto_fixed: Why Rekono fixed it, or None when a user did it.
        fixed_date: Moment when the finding was fixed.
        fixed_by: User that fixed the finding.
        created_from_user_input: Whether the finding comes from the data that the
          auditor provided, instead of from a tool.
        objects: Manager that deduplicates the findings and fixes the ones that
          stop being discovered.
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
        """Model configuration, marking it as abstract."""

        abstract = True

    @dataclass
    class UniqueField:
        """Field that takes part in the identification of the duplicated findings.

        Attributes:
            field: Model field to match on.
            match_null_and_empty: Whether a blank value (null or, for char/text fields, empty)
              is treated as compatible with anything on this field: an existing finding blank on it
              matches an incoming real value, and an incoming blank value drops it from the match.
            ignore_case: Whether a string value is matched case-insensitively, so findings that
              differ only in the casing of this field are treated as the same. Only meaningful for
              char/text fields whose casing is cosmetic (e.g. a technology name); it must stay off for
              fields where case is significant (paths, usernames, secrets).
        """

        field: str
        match_null_and_empty: bool = False
        ignore_case: bool = False

    @classmethod
    def _find_duplicate(cls, execution: Execution, fields: dict[str, Any]) -> "Finding | None":
        """Find an existing finding that duplicates the incoming one, or None.

        Matches on every ``_unique_fields`` value for the same target. A ``match_null_and_empty``
        field is dropped when the incoming value is blank, and otherwise also matches existing blanks
        so a partial finding can be completed. Complex finding types override this method.

        Args:
            execution: Execution that discovered the finding.
            fields: Values of the finding that is being created.

        Returns:
            The finding that was already discovered, or None if this one is new.
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
        char/text fields) so a partial finding can still be completed by a more detailed one. An
        ``ignore_case`` field matches string values case-insensitively.

        Args:
            unique_field: Field whose query fragment is built.
            new_value: Value reported for that field.

        Returns:
            The query fragment, or None when the field doesn't constrain the match.
        """
        if unique_field.match_null_and_empty and new_value in (None, ""):
            return
        field_query = Q(
            **{
                f"{unique_field.field}__iexact"
                if unique_field.ignore_case and isinstance(new_value, str)
                else unique_field.field: new_value
            }
        )
        if unique_field.match_null_and_empty:
            field_query |= Q(**{f"{unique_field.field}__isnull": True})
            if cls._meta.get_field(unique_field.field).get_internal_type() in ["CharField", "TextField"]:
                field_query |= Q(**{unique_field.field: ""})
        return field_query

    @cached_property
    def parent_project(self) -> Project:
        """The project that the finding belongs to, through its first execution."""
        return self.executions.first().task.target.project

    def _apply_defectdojo_mapping(self, mapping: dict[str, Any]) -> dict[str, Any]:
        """Build the data that DefectDojo expects, from a field mapping.

        Args:
            mapping: DefectDojo field names and how to fill each one. A callable is
              invoked with the finding, a string that names one of its attributes is
              replaced by that attribute, and anything else is used as it is.

        Returns:
            The data to be sent to DefectDojo. A string that doesn't name an
            attribute of the finding stays in it as a literal value, so a mistyped
            attribute name is sent instead of raising.
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
        """Get this finding in the format that DefectDojo imports.

        The severity is emitted as its DefectDojo label ("Info", "Low", "Medium",
        "High", "Critical") as required by the import endpoints.

        Returns:
            The finding fields that DefectDojo expects, already mapped.
        """
        default_mapping = {"active": lambda instance: not instance.is_fixed, "is_mitigated": "is_fixed"}
        # TriageFinding subclasses also report verified/false positive/risk accepted status,
        # and redefine "active" to additionally require an untriaged or true positive status
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
        data = self._apply_defectdojo_mapping({**self._defectdojo_finding_mapping, **default_mapping})
        if data.get("severity") is not None:
            data["severity"] = str(Severity(int(data["severity"])))
        return data

    def defectdojo_endpoint(self) -> dict[str, Any]:
        """Get the endpoint of this finding in the format that DefectDojo imports.

        Returns:
            The endpoint fields that DefectDojo expects, which is empty for the
            findings that don't identify one.
        """
        return self._apply_defectdojo_mapping(self._defectdojo_endpoint_mapping)

    def __str__(self) -> str:
        """Return the values that identify the finding, joined by " - "."""
        return " - ".join(
            [
                getattr(self, unique_field.field).__str__()
                for unique_field in self.__class__._unique_fields
                if getattr(self, unique_field.field)
            ]
        )


class HacktricksFinding(Finding):
    """Base model of the findings that can be linked to a HackTricks guide.

    Only the findings whose characteristics can be mapped to a guide, which are the
    hosts, the ports, and the technologies, extend this model.

    Attributes:
        hacktricks_link: Link to the HackTricks guide about this finding.
    """

    hacktricks_link = TextField(max_length=300, blank=True, null=True)

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True


class TriageFinding(Finding):
    """Base model of the findings that the auditors review one by one.

    Attributes:
        triage_status: Conclusion of the review, untriaged until someone reviews it.
        triage_comment: Explanation of that conclusion.
        triage_date: Moment when the finding was reviewed.
        triage_by: User that reviewed the finding.
    """

    triage_status = TextField(max_length=15, choices=TriageStatus.choices, default=TriageStatus.UNTRIAGED)
    triage_comment = TextField(
        max_length=300, validators=[Validator(Regex.TEXT, code="triage_comment")], blank=True, null=True
    )
    triage_date = DateTimeField(blank=True, null=True)
    triage_by = ForeignKey(AUTH_USER_MODEL, related_name="triaged_%(class)s", on_delete=SET_NULL, blank=True, null=True)

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True

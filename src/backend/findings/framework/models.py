from typing import Any, Dict, List

from django.core.exceptions import NON_FIELD_ERRORS
from django.db import connection, models
from executions.models import Execution
from findings.enums import TriageStatus
from framework.models import BaseInput
from security.input_validator import Regex, Validator


class Finding(BaseInput):
    executions = models.ManyToManyField(
        Execution,
        related_name="%(class)s",
    )
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    triage_status = models.TextField(
        max_length=15, choices=TriageStatus.choices, default=TriageStatus.UNTRIAGED
    )
    triage_comment = models.TextField(
        max_length=300, validators=[Validator(Regex.TEXT.value, code="triage_comment")]
    )
    defect_dojo_id = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def get_unique_fields(cls) -> List[str]:
        for constraint in (cls._meta.original_attrs or {}).get("constraints", []):
            if isinstance(constraint, models.UniqueConstraint):
                return list(constraint.fields)
        return []

    # Method copied from https://github.com/django/django/blob/main/django/db/models/base.py#L1343
    def _perform_unique_checks(self, unique_checks):
        errors = {}
        for model_class, unique_check in unique_checks:
            # Line modified to require findings to be unique by target
            lookup_kwargs = {
                "executions__task__target__in": self.executions.all().select_related(
                    "task__target"
                )
            }
            for field_name in unique_check:
                f = self._meta.get_field(field_name)
                lookup_value = getattr(self, f.attname)
                if lookup_value is None or (
                    lookup_value == ""
                    and connection.features.interprets_empty_strings_as_nulls
                ):
                    continue
                if f.primary_key and not self._state.adding:
                    continue
                lookup_kwargs[str(field_name)] = lookup_value
            if len(unique_check) != len(lookup_kwargs):
                continue
            qs = model_class._default_manager.filter(**lookup_kwargs)
            model_class_pk = self._get_pk_val(model_class._meta)
            if not self._state.adding and model_class_pk is not None:
                qs = qs.exclude(pk=model_class_pk)
            if qs.exists():
                if len(unique_check) == 1:
                    key = unique_check[0]
                else:
                    key = NON_FIELD_ERRORS
                errors.setdefault(key, []).append(
                    self.unique_error_message(model_class, unique_check)
                )
        return errors

    def get_project(self) -> Any:
        return self.executions.first().task.target.project

    @classmethod
    def get_project_field(cls) -> str:
        return "executions__task__target__project"

    def defect_dojo(self) -> Dict[str, Any]:
        pass

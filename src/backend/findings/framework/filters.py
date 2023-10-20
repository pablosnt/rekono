from django_filters.filters import ModelChoiceFilter
from findings.models import OSINT
from framework.filters import MultipleFieldFilterSet


class FindingFilter(MultipleFieldFilterSet):
    tool = ModelChoiceFilter(field_name="executions__configuration__tool")
    task = ModelChoiceFilter(field_name="executions__task")
    target = ModelChoiceFilter(field_name="executions__task__target")
    project = ModelChoiceFilter(field_name="executions__task__target__project")
    executor = ModelChoiceFilter(field_name="executions__task__executor")

    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = {
            "executions": ["exact"],
            "first_seen": ["gte", "lte", "exact"],
            "last_seen": ["gte", "lte", "exact"],
            "triage_status": ["exact"],
            "triage_comment": ["exact", "icontains"],
        }

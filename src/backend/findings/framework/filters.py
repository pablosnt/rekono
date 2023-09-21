from findings.models import OSINT
from framework.filters import MultipleFieldFilterSet


class FindingFilter(MultipleFieldFilterSet):
    class Meta:
        model = OSINT  # It's needed to define a non-abstract model as default. It will be overwritten
        fields = {
            "executions": ["exact"],
            "executions__configuration__tool": ["exact"],
            "executions__configuration__tool__name": ["exact", "icontains"],
            "executions__task": ["exact"],
            "executions__task__target": ["exact"],
            "executions__task__target__target": ["exact", "icontains"],
            "executions__task__target__project": ["exact"],
            "executions__task__target__project__name": ["exact", "icontains"],
            "executions__task__executor": ["exact"],
            "executions__task__executor__username": ["exact", "icontains"],
            "first_seen": ["gte", "lte", "exact"],
            "last_seen": ["gte", "lte", "exact"],
            "triage_status": ["exact"],
            "triage_comment": ["exact", "icontains"],
        }

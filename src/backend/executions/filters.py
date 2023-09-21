from django_filters.rest_framework import FilterSet
from executions.models import Execution


class ExecutionFilter(FilterSet):
    class Meta:
        model = Execution
        fields = {
            "task": ["exact"],
            "task__target": ["exact"],
            "task__target__target": ["exact", "icontains"],
            "task__target__project": ["exact"],
            "task__target__project__name": ["exact", "icontains"],
            "task__process": ["exact"],
            "group": ["exact"],
            "task__process__name": ["exact", "icontains"],
            "task__intensity": ["exact"],
            "task__executor": ["exact"],
            "task__executor__username": ["exact", "icontains"],
            "configuration": ["exact"],
            "configuration__name": ["exact", "icontains"],
            "configuration__tool": ["exact"],
            "configuration__tool__name": ["exact", "icontains"],
            "configuration__stage": ["exact"],
            "status": ["exact"],
            "enqueued_at": ["gte", "lte", "exact"],
            "start": ["gte", "lte", "exact"],
            "end": ["gte", "lte", "exact"],
        }

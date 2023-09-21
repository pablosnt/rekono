from django_filters.rest_framework import FilterSet
from tasks.models import Task


class TaskFilter(FilterSet):
    class Meta:
        model = Task
        fields = {
            "target": ["exact"],
            "target__target": ["exact", "icontains"],
            "target__project": ["exact"],
            "target__project__name": ["exact", "icontains"],
            "process": ["exact"],
            "process__name": ["exact", "icontains"],
            "configuration": ["exact"],
            "configuration__name": ["exact", "icontains"],
            "configuration__tool": ["exact"],
            "configuration__tool__name": ["exact", "icontains"],
            "configuration__stage": ["exact"],
            "intensity": ["exact"],
            "executor": ["exact"],
            "executor__username": ["exact", "icontains"],
            "creation": ["gte", "lte", "exact"],
            "enqueued_at": ["gte", "lte", "exact"],
            "start": ["gte", "lte", "exact"],
            "end": ["gte", "lte", "exact"],
        }

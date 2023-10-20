from django_filters.filters import ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from tasks.models import Task


class TaskFilter(FilterSet):
    project = ModelChoiceFilter(field_name="target__project")
    tool = ModelChoiceFilter(field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage")

    class Meta:
        model = Task
        fields = {
            "target": ["exact"],
            "process": ["exact"],
            "configuration": ["exact"],
            "intensity": ["exact"],
            "executor": ["exact"],
            "creation": ["gte", "lte", "exact"],
            "enqueued_at": ["gte", "lte", "exact"],
            "start": ["gte", "lte", "exact"],
            "end": ["gte", "lte", "exact"],
        }

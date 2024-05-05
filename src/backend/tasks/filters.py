from django_filters.filters import ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from projects.models import Project
from tasks.models import Task
from tools.enums import Stage
from tools.models import Tool


class TaskFilter(FilterSet):
    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project"
    )
    tool = ModelChoiceFilter(
        queryset=Tool.objects.all(), field_name="configuration__tool"
    )
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)

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

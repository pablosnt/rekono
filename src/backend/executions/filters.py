from django_filters.filters import ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from executions.models import Execution


class ExecutionFilter(FilterSet):
    target = ModelChoiceFilter(field_name="task__target")
    project = ModelChoiceFilter(field_name="task__target__project")
    process = ModelChoiceFilter(field_name="task__process")
    tool = ModelChoiceFilter(field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage")
    intensity = ChoiceFilter(field_name="task__intensity")
    executor = ModelChoiceFilter(field_name="task__executor")

    class Meta:
        model = Execution
        fields = {
            "task": ["exact", "isnull"],
            "group": ["exact"],
            "configuration": ["exact"],
            "status": ["exact"],
            "enqueued_at": ["gte", "lte", "exact"],
            "start": ["gte", "lte", "exact"],
            "end": ["gte", "lte", "exact"],
        }

from django_filters.filters import ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from executions.models import Execution
from processes.models import Process
from projects.models import Project
from targets.models import Target
from tools.enums import Intensity, Stage
from tools.models import Tool
from users.models import User


class ExecutionFilter(FilterSet):
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="task__target")
    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="task__target__project"
    )
    process = ModelChoiceFilter(
        queryset=Process.objects.all(), field_name="task__process"
    )
    tool = ModelChoiceFilter(
        queryset=Tool.objects.all(), field_name="configuration__tool"
    )
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)
    intensity = ChoiceFilter(field_name="task__intensity", choices=Intensity.choices)
    executor = ModelChoiceFilter(
        queryset=User.objects.all(), field_name="task__executor"
    )

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

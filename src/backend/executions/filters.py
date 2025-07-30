"""Django REST framework filters for execution models.

This module provides filtering capabilities for execution records,
allowing users to filter execution data by various criteria such
as target, project, process, tool, stage, intensity, and executor.
"""

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
    """Filter set for Execution model.

    This class provides filtering capabilities for execution records,
    allowing filtering by target, project, process, tool, stage,
    intensity, executor, and various time-based criteria.

    Attributes:
        target (ModelChoiceFilter): Filter by target associated with the execution.
        project (ModelChoiceFilter): Filter by project associated with the execution.
        process (ModelChoiceFilter): Filter by process associated with the execution.
        tool (ModelChoiceFilter): Filter by tool used in the execution.
        stage (ChoiceFilter): Filter by execution stage.
        intensity (ChoiceFilter): Filter by execution intensity level.
        executor (ModelChoiceFilter): Filter by user who executed the task.
    """

    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="task__target")
    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="task__target__project")
    process = ModelChoiceFilter(queryset=Process.objects.all(), field_name="task__process")
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)
    intensity = ChoiceFilter(field_name="task__intensity", choices=Intensity.choices)
    executor = ModelChoiceFilter(queryset=User.objects.all(), field_name="task__executor")

    class Meta:
        """Meta configuration for the ExecutionFilter.

        Attributes:
            model: The Execution model to filter.
            fields: Dictionary defining available filters and their lookup types.
        """

        model = Execution
        fields = {
            "task": ["exact"],
            "configuration": ["exact"],
            "status": ["exact"],
            "enqueued_at": ["gte", "lte", "exact"],
            "start": ["gte", "lte", "exact"],
            "end": ["gte", "lte", "exact"],
        }

"""Django REST framework filters for execution models.

Provides filtering capabilities for execution records by target, project,
process, tool, stage, intensity, and executor criteria.
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

    Provides filtering capabilities for execution records by target, project,
    process, tool, stage, intensity, executor, and time-based criteria.

    Attributes:
        target (ModelChoiceFilter): Filter by associated target
        project (ModelChoiceFilter): Filter by associated project
        process (ModelChoiceFilter): Filter by associated process
        tool (ModelChoiceFilter): Filter by tool used in execution
        stage (ChoiceFilter): Filter by execution stage
        intensity (ChoiceFilter): Filter by execution intensity level
        executor (ModelChoiceFilter): Filter by user who executed the task
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
            model (Model): The Execution model to filter
            fields (dict): Available filters and their lookup types
        """

        model = Execution
        fields = {
            "task": ["exact"],
            "configuration": ["exact"],
            "status": ["exact"],
            "enqueued_at": ["gte", "lte", "exact"],
            "start": ["gte", "lte", "exact"],
            "end": ["gte", "lte", "exact"],
            "osint": ["exact"],
            "host": ["exact"],
            "port": ["exact"],
            "path": ["exact"],
            "technology": ["exact"],
            "credential": ["exact"],
            "vulnerability": ["exact"],
            "exploit": ["exact"],
        }

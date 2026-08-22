"""Filters of the task endpoints."""

from django_filters.filters import ChoiceFilter, ModelChoiceFilter

from framework.filters import MultipleFieldFilterSet, MultipleModelFilter
from projects.models import Project
from tasks.models import Task
from tools.enums import Stage
from tools.models import Configuration, Tool


class TaskFilter(MultipleFieldFilterSet):
    """Filters to search tasks by their target, their tools, and their dates.

    Attributes:
        project: Filter by the project that owns the target.
        executed_configuration: Filter by a configuration executed by the task,
          either directly or as a step of its process.
        executed_tool: Filter by a tool executed by the task, either directly or as
          a step of its process.
        tool: Filter by the tool of the configuration that the task executes.
        stage: Filter by the stage of that tool.
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="target__project")
    executed_configuration = MultipleModelFilter(
        queryset=Configuration.objects.all(), fields=["configuration", "process__steps__configuration"]
    )
    executed_tool = MultipleModelFilter(
        queryset=Tool.objects.all(), fields=["configuration__tool", "process__steps__configuration__tool"]
    )
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)

    class Meta:
        """Filter configuration for the tasks."""

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

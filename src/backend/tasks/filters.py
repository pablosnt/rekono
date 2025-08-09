"""Django filter classes for task model queries.

Provides filtering capabilities for task API endpoints with support for
project, tool, stage, and various time-based filtering operations.
"""

from django_filters.filters import ChoiceFilter, ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from tasks.models import Task
from tools.enums import Stage
from tools.models import Tool


class TaskFilter(FilterSet):
    """Filter class for Task model queries.

    Provides comprehensive filtering options for task queries including
    project filtering, tool filtering, configuration stages, and time-based filtering.

    Attributes:
        project (ModelChoiceFilter): Filter by project through target relationship
        tool (ModelChoiceFilter): Filter by specific tool through configuration
        stage (ChoiceFilter): Filter by tool execution stage
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="target__project")
    tool = ModelChoiceFilter(queryset=Tool.objects.all(), field_name="configuration__tool")
    stage = ChoiceFilter(field_name="configuration__stage", choices=Stage.choices)

    class Meta:
        """Meta configuration for TaskFilter.

        Attributes:
            model (Model): The Task model to filter
            fields (dict): Available filter fields and their lookup types
        """

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

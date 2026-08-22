"""Base filters of the input parameter endpoints."""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from targets.models import Target


class InputParameterFilter(FilterSet):
    """Base filters to search parameters by where they are used.

    Attributes:
        project: Filter by the project of the tasks that use the parameter.
        target: Filter by the target of those tasks.
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="tasks__target__project")
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="tasks__target")

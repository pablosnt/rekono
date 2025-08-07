"""Django filters for parameter framework models.

Filter classes for querying and filtering parameter objects in the REST API.
Provides relationship-based filtering capabilities for parameter searches
across projects and targets.
"""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from targets.models import Target


class InputParameterFilter(FilterSet):
    """Filter class for input parameter models.

    Provides filtering capabilities for parameter queries based on associated
    projects and targets through task relationships.

    Attributes:
        project (ModelChoiceFilter): Filter by project through task relationships
        target (ModelChoiceFilter): Filter by target through task relationships
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="tasks__target__project")
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="tasks__target")

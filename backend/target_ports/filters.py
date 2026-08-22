"""Filters of the target port endpoints."""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from target_ports.models import TargetPort


class TargetPortFilter(FilterSet):
    """Filters to search target ports by their target, port, and path.

    Attributes:
        project: Filter by the project that owns the target.
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="target__project")

    class Meta:
        """Filter configuration for the target ports."""

        model = TargetPort
        fields = {"target": ["exact"], "port": ["exact"], "path": ["exact", "icontains"]}

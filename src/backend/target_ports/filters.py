from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from projects.models import Project
from target_ports.models import TargetPort


class TargetPortFilter(FilterSet):
    """FilterSet to filter and sort Target Port entities."""

    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project"
    )

    class Meta:
        """FilterSet metadata."""

        model = TargetPort
        fields = {
            "target": ["exact"],
            "port": ["exact"],
            "path": ["exact", "icontains"],
        }

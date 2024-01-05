from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from parameters.models import InputTechnology, InputVulnerability
from projects.models import Project


class InputTechnologyFilter(FilterSet):
    """FilterSet to filter and sort input Technology entities."""

    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project"
    )

    class Meta:
        model = InputTechnology
        fields = {
            "target": ["exact"],
            "name": ["exact", "icontains"],
            "version": ["exact", "icontains"],
        }


class InputVulnerabilityFilter(FilterSet):
    """FilterSet to filter and sort input Vulnerability entities."""

    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project"
    )

    class Meta:
        model = InputVulnerability
        fields = {
            "target": ["exact"],
            "cve": ["exact"],
        }

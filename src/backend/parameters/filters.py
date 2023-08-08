from django_filters.rest_framework import FilterSet
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologyFilter(FilterSet):
    """FilterSet to filter and sort input Technology entities."""

    class Meta:
        model = InputTechnology
        fields = {  # Filter fields
            "target": ["exact"],
            "target__project": ["exact"],
            "target__project__name": ["exact", "icontains"],
            "target__target": ["exact"],
            "name": ["exact", "icontains"],
            "version": ["exact", "icontains"],
        }


class InputVulnerabilityFilter(FilterSet):
    """FilterSet to filter and sort input Vulnerability entities."""

    class Meta:
        model = InputVulnerability
        fields = {  # Filter fields
            "target": ["exact"],
            "target__project": ["exact"],
            "target__project__name": ["exact", "icontains"],
            "target__target": ["exact"],
            "cve": ["exact"],
        }

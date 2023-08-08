from django_filters.rest_framework import FilterSet
from target_ports.models import TargetPort


class TargetPortFilter(FilterSet):
    """FilterSet to filter and sort Target Port entities."""

    class Meta:
        """FilterSet metadata."""

        model = TargetPort
        fields = {  # Filter fields
            "target": ["exact"],
            "target__project": ["exact"],
            "target__project__name": ["exact", "icontains"],
            "target__target": ["exact", "icontains"],
            "port": ["exact"],
        }

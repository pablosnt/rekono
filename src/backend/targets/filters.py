from django_filters.rest_framework import FilterSet
from targets.models import Target


class TargetFilter(FilterSet):
    """FilterSet to filter and sort Target entities."""

    class Meta:
        model = Target
        fields = {
            "project": ["exact"],
            "project__name": ["exact", "icontains"],
            "target": ["exact", "icontains"],
            "type": ["exact"],
        }

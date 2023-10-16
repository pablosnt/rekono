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
            "defect_dojo_sync": ["exact"],
            "defect_dojo_sync__engagement_id": ["exact"],
            "defect_dojo_sync__defect_dojo_sync__product_type_id": ["exact"],
            "defect_dojo_sync__defect_dojo_sync__product_id": ["exact"],
        }

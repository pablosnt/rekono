from django_filters.filters import NumberFilter
from django_filters.rest_framework import FilterSet
from targets.models import Target


class TargetFilter(FilterSet):
    """FilterSet to filter and sort Target entities."""

    defect_dojo_product_type = NumberFilter(
        field_name="defect_dojo_sync__defect_dojo_sync__product_type_id"
    )
    defect_dojo_product = NumberFilter(
        field_name="defect_dojo_sync__defect_dojo_sync__product_id"
    )
    defect_dojo_engagement = NumberFilter(field_name="defect_dojo_sync__engagement_id")

    class Meta:
        model = Target
        fields = {
            "project": ["exact"],
            "target": ["exact", "icontains"],
            "type": ["exact"],
            "defect_dojo_sync": ["exact"],
        }

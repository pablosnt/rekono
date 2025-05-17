from django_filters.filters import NumberFilter
from django_filters.rest_framework import FilterSet
from targets.models import Target


class TargetFilter(FilterSet):
    """FilterSet to filter and sort Target entities."""

    defectdojo_product_type = NumberFilter(field_name="defectdojo_sync__defectdojo_sync__product_type_id")
    defectdojo_product = NumberFilter(field_name="defectdojo_sync__defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")

    class Meta:
        model = Target
        fields = {
            "project": ["exact"],
            "target": ["exact", "icontains"],
            "type": ["exact"],
            "defectdojo_sync": ["exact"],
        }

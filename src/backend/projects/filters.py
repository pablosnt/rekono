from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project


class ProjectFilter(FilterSet):
    """FilterSet to filter Project entities."""

    tag = CharFilter(field_name="tags__name", lookup_expr="in")
    defect_dojo_product_type = NumberFilter(
        field_name="defect_dojo_sync__product_type_id"
    )
    defect_dojo_product = NumberFilter(field_name="defect_dojo_sync__product_id")
    defect_dojo_engagement = NumberFilter(field_name="defect_dojo_sync__engagement_id")

    class Meta:
        model = Project
        fields = {
            "name": ["exact", "icontains"],
            "owner": ["exact"],
            "members": ["exact"],
            "defect_dojo_sync": ["exact"],
        }

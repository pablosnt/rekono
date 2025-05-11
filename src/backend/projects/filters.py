from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from projects.models import Project


class ProjectFilter(FilterSet):
    """FilterSet to filter Project entities."""

    tag = CharFilter(field_name="tags__name")
    defectdojo_product_type = NumberFilter(field_name="defectdojo_sync__product_type_id")
    defectdojo_product = NumberFilter(field_name="defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")

    class Meta:
        model = Project
        fields = {
            "name": ["exact", "icontains"],
            "owner": ["exact"],
            "members": ["exact"],
            "defectdojo_sync": ["exact"],
        }

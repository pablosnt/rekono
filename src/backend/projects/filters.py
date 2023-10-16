from django_filters.rest_framework import FilterSet
from projects.models import Project


class ProjectFilter(FilterSet):
    """FilterSet to filter Project entities."""

    class Meta:
        model = Project
        fields = {
            "name": ["exact", "icontains"],
            "owner": ["exact"],
            "owner__username": ["exact"],
            "members": ["exact"],
            "tags__name": ["in"],
            "defect_dojo_sync": ["exact"],
            "defect_dojo_sync__product_type_id": ["exact"],
            "defect_dojo_sync__product_id": ["exact"],
            "defect_dojo_sync__engagement_id": ["exact"],
            "defect_dojo_sync__engagement_per_target": ["exact"],
        }

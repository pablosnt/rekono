"""Filters of the target endpoints."""

from django_filters.filters import NumberFilter
from django_filters.rest_framework import FilterSet

from targets.models import Target


class TargetFilter(FilterSet):
    """Filters to search targets by their data and their DefectDojo synchronization.

    Attributes:
        defectdojo_product: Filter by the DefectDojo product that the project of the
          target is synchronized with.
        defectdojo_engagement: Filter by the DefectDojo engagement that the target
          is synchronized with.
    """

    defectdojo_product = NumberFilter(field_name="defectdojo_sync__defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")

    class Meta:
        """Filter configuration for the targets."""

        model = Target
        fields = {
            "project": ["exact"],
            "target": ["exact", "icontains"],
            "type": ["exact"],
            "defectdojo_sync": ["exact"],
        }

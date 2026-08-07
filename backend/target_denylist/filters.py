"""Filters of the target denylist endpoints."""

from django_filters.rest_framework import FilterSet

from target_denylist.models import TargetDenylist


class TargetDenylistFilter(FilterSet):
    """Filters to search denylist entries by their value and their origin."""

    class Meta:
        """Filter configuration for the denylist entries."""

        model = TargetDenylist
        fields = {"target": ["exact", "icontains"], "default": ["exact"]}

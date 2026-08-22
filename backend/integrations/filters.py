"""Filters of the integration endpoints."""

from django_filters.rest_framework import FilterSet

from integrations.models import Integration


class IntegrationFilter(FilterSet):
    """Filters to search the external platforms."""

    class Meta:
        """Filter configuration for the integrations."""

        model = Integration
        fields = {"name": ["exact", "icontains"], "enabled": ["exact"]}

"""Filters for the integrations app.

This module provides Django REST Framework filters for the Integration model,
enabling advanced query filtering and search capabilities for integration data.
"""

from django_filters.rest_framework import FilterSet

from integrations.models import Integration


class IntegrationFilter(FilterSet):
    """FilterSet for the Integration model.

    This filter set provides advanced filtering capabilities for Integration
    instances through the API. It supports exact and case-insensitive contains
    matching for text fields, and exact matching for boolean fields.

    The filter enables users to search for integrations by name (exact or
    partial matches) and filter by enabled status to show only active or
    inactive integrations.
    """

    class Meta:
        """Meta configuration for the IntegrationFilter.

        This inner class defines the filter's configuration, specifying
        which model to filter and which fields support which types of
        filtering operations.

        Attributes:
            model: The Django model class to filter (Integration).
            fields: Dictionary mapping field names to list of filter types.
        """

        model = Integration
        fields = {"name": ["exact", "icontains"], "enabled": ["exact"]}

"""Django filters for integration REST API endpoints.

Provides filtering capabilities for integration API queries including
name-based filtering and enabled status filtering.
"""

from django_filters.rest_framework import FilterSet

from integrations.models import Integration


class IntegrationFilter(FilterSet):
    """Filter class for Integration model queries.

    Provides filtering options for integration API endpoints with support
    for name matching and enabled status filtering.
    """

    class Meta:
        """Meta configuration for the IntegrationFilter.

        Attributes:
            model (Model): The Integration model to filter
            fields (dict): Field names and their supported filter operations
        """

        model = Integration
        fields = {"name": ["exact", "icontains"], "enabled": ["exact"]}

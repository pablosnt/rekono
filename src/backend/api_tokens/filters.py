"""Filters for API token queries."""

from django_filters.rest_framework import FilterSet

from api_tokens.models import ApiToken


class ApiTokenFilter(FilterSet):
    """FilterSet to filter API token entities by name and expiration."""

    class Meta:
        """Meta configuration for the ApiTokenFilter.

        Attributes:
            model: The ApiToken model to filter.
            fields: Dictionary defining available filters and their lookup types.
        """

        model = ApiToken
        fields = {
            "name": ["exact", "icontains"],
            "expiration": ["gte", "lte", "exact"],
        }

"""Filters of the API token endpoints."""

from django_filters.rest_framework import FilterSet

from api_tokens.models import ApiToken


class ApiTokenFilter(FilterSet):
    """Filters to search API tokens by name and expiration date."""

    class Meta:
        """Filter configuration for the API tokens."""

        model = ApiToken
        fields = {
            "name": ["exact", "icontains"],
            "expiration": ["gte", "lte", "exact"],
        }

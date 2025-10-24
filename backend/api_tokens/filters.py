"""Filters for API token queries.

Provides filtering capabilities for API token searches including
name and expiration date filtering with various lookup types.
"""

from django_filters.rest_framework import FilterSet

from api_tokens.models import ApiToken


class ApiTokenFilter(FilterSet):
    """FilterSet for filtering API token entities.

    Provides filtering by name (exact and partial matches) and expiration
    date (greater than, less than, and exact matches).
    """

    class Meta:
        """Meta configuration for the ApiTokenFilter.

        Attributes:
            model (Model): The ApiToken model to filter
            fields (dict): Available filters and their lookup types
        """

        model = ApiToken
        fields = {
            "name": ["exact", "icontains"],
            "expiration": ["gte", "lte", "exact"],
        }

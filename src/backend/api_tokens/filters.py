from django_filters.rest_framework import FilterSet

from api_tokens.models import ApiToken


class ApiTokenFilter(FilterSet):
    """FilterSet to filter Project entities."""

    class Meta:
        model = ApiToken
        fields = {
            "name": ["exact", "icontains"],
            "expiration": ["gte", "lte", "exact"],
        }

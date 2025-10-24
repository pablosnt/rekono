"""Django filters for target denylist query operations.

Provides filtering capabilities for target denylist API endpoints with
support for exact matching and text search operations.
"""

from django_filters.rest_framework import FilterSet

from target_denylist.models import TargetDenylist


class TargetDenylistFilter(FilterSet):
    """Filter class for TargetDenylist model queries.

    Provides filtering options for target denylist API endpoints including
    exact matching for target patterns and default status filtering.
    """

    class Meta:
        """Meta configuration for TargetDenylistFilter.

        Attributes:
            model (type): TargetDenylist model class.
            fields (dict): Available filter fields with their supported operations.
        """

        model = TargetDenylist
        fields = {"target": ["exact", "icontains"], "default": ["exact"]}

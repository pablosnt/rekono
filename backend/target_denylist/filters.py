"""Django filters for target denylist query operations.

Provides filtering capabilities for target denylist API endpoints with
support for exact matching and text search operations.
"""

from django_filters.rest_framework import FilterSet

from target_denylist.models import TargetDenylist


class TargetDenylistFilter(FilterSet):
    """Filter class for TargetDenylist model queries.

    Provides filtering options for target denylist API endpoints including
    exact and partial, case-insensitive text search on target patterns, plus
    exact matching on the default status flag.
    """

    class Meta:
        """Meta configuration for TargetDenylistFilter.

        Attributes:
            model (Model): The TargetDenylist model to filter.
            fields (dict): Available filter fields and their lookup types.
        """

        model = TargetDenylist
        fields = {"target": ["exact", "icontains"], "default": ["exact"]}

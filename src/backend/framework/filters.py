"""This module implements filtering utilities."""

from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import BooleanFilter, CharFilter, Filter, NumberFilter


class LikeFilter(FilterSet):
    """Filter set for likeable entities.

    This filter set provides filtering capabilities for entities that can be
    liked by users. It includes a boolean filter to show only liked or
    unliked entities.

    Attributes:
        like (BooleanFilter): Filter to show only liked or unliked entities.
    """

    # Indicate if user likes or not the entities
    like = BooleanFilter(method="get_liked_items")

    def get_liked_items(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Filter queryset by like status.

        Args:
            queryset: The base queryset to filter.
            name: The filter field name.
            value: True to show only liked items, False for unliked.

        Returns:
            Filtered queryset based on like status.
        """
        liked = {"liked_by": self.request.user}
        return queryset.filter(Q(**liked) if value else ~Q(**liked)).all()


class MultipleFieldFilterSet(FilterSet):
    """Base filter set for multiple field filtering.

    This abstract base class provides functionality for filtering across
    multiple fields using a single filter value.
    """

    def multiple_field_filter(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        """Filter queryset across multiple fields.

        Applies the filter value to all configured fields using OR logic.

        Args:
            queryset: The base queryset to filter.
            name: The filter field name.
            value: The value to search for across multiple fields.

        Returns:
            Filtered queryset matching any of the configured fields.
        """
        query = Q()
        for field in self.filters[name].fields:
            query |= Q(**{field: value})
        return queryset.filter(query)


class MultipleFieldFilter(Filter):
    """Filter that searches across multiple fields.

    This filter applies a single value to multiple database fields
    using OR logic.

    Attributes:
        fields (list[str]): List of field names to search across.
    """

    def __init__(self, fields: list[str], **kwargs: Any) -> None:
        """Initialize the multiple field filter.

        Args:
            fields: List of field names to search across.
            **kwargs: Additional filter configuration.
        """
        self.fields = fields
        kwargs["method"] = "multiple_field_filter"
        super().__init__(**kwargs)


class MultipleNumberFilter(MultipleFieldFilter, NumberFilter):
    """Multiple field filter for numeric values.

    Extends MultipleFieldFilter to handle numeric field filtering.
    """

    pass


class MultipleCharFilter(MultipleFieldFilter, CharFilter):
    """Multiple field filter for character values.

    Extends MultipleFieldFilter to handle character field filtering.
    """

    pass

"""Custom filter classes for Django REST framework API endpoints.

Provides specialized filter implementations for like functionality
and multiple field filtering capabilities.
"""

from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import BooleanFilter, CharFilter, Filter, ModelChoiceFilter, NumberFilter


class LikeFilter(FilterSet):
    """Filter for models with like/favorite functionality.

    Provides filtering based on whether the current user has liked
    the objects in the queryset.

    Attributes:
        like (BooleanFilter): Filter for liked/unliked objects.
    """

    like = BooleanFilter(method="get_liked_items")

    def get_liked_items(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Filter queryset based on user's like status.

        Args:
            queryset (QuerySet): The base queryset to filter.
            name (str): The filter field name (unused).
            value (bool): True to get liked items, False for unliked items.

        Returns:
            QuerySet: Filtered queryset based on like status.
        """
        liked = {"liked_by": self.request.user}
        return queryset.filter(Q(**liked) if value else ~Q(**liked)).all()


class MultipleFieldFilterSet(FilterSet):
    """FilterSet with support for multiple field filtering.

    Base FilterSet class that provides the ability to filter across
    multiple fields with a single filter parameter.
    """

    def multiple_field_filter(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        """Filter queryset across multiple fields with OR logic.

        Args:
            queryset (QuerySet): The base queryset to filter.
            name (str): Name of the filter attribute on this FilterSet, used to
                        look up its `fields` list in self.filters.
            value (Any): The value to search for in all specified fields.

        Returns:
            QuerySet: Filtered queryset matching value in any specified field.
        """
        query = Q()
        for field in self.filters[name].fields:
            query |= Q(**{field: value})
        return queryset.filter(query)


class MultipleFieldFilter(Filter):
    """Base filter for searching across multiple fields.

    Allows filtering a queryset by searching for a value across
    multiple model fields using OR logic.

    Attributes:
        fields (list[str]): List of field names to search across.
    """

    def __init__(self, fields: list[str], **kwargs: Any) -> None:
        """Initialize the multiple field filter.

        Args:
            fields (list[str]): List of field names to search across.
            **kwargs (Any): Additional filter arguments.
        """
        self.fields = fields
        # Method defined in MultipleFieldFilterSet
        kwargs["method"] = "multiple_field_filter"
        super().__init__(**kwargs)


class MultipleNumberFilter(MultipleFieldFilter, NumberFilter):
    """Multiple field filter for numeric values.

    Combines MultipleFieldFilter with NumberFilter to enable
    searching for numeric values across multiple fields.

    Example:
        ```python
        class MyFilterSet(MultipleFieldFilterSet):
            port_search = MultipleNumberFilter(fields=["port", "target_port"])
        ```
    """

    pass


class MultipleCharFilter(MultipleFieldFilter, CharFilter):
    """Multiple field filter for character/string values.

    Combines MultipleFieldFilter with CharFilter to enable
    searching for string values across multiple fields.

    Example:
        ```python
        class MyFilterSet(MultipleFieldFilterSet):
            name_search = MultipleCharFilter(fields=["name", "title", "description"])
        ```
    """

    pass


class MultipleModelFilter(MultipleFieldFilter, ModelChoiceFilter):
    """Multiple field filter for model object values.

    Combines MultipleFieldFilter with ModelChoiceFilter to enable
    filtering by a model instance across multiple relationship fields.

    Example:
        ```python
        class MyFilterSet(MultipleFieldFilterSet):
            tool_search = MultipleModelFilter(
                queryset=Tool.objects.all(),
                fields=["configuration__tool", "process__steps__configuration__tool"],
            )
        ```
    """

    pass

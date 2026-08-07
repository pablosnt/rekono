"""Custom filters shared by the Rekono API endpoints.

Cover the two filtering needs that aren't solved by the standard django-filter
classes: filtering by the likes of the user that performs the request, and
searching a single value across several model fields.
"""

from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import BooleanFilter, CharFilter, Filter, ModelChoiceFilter, NumberFilter


class LikeFilter(FilterSet):
    """Base filter set for the models that can be liked by the users.

    Attributes:
        like: Whether to return only the objects liked by the user that performs
          the request, or only the ones that aren't liked.
    """

    like = BooleanFilter(method="get_liked_items")

    def get_liked_items(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Filter the objects by the likes of the user that performs the request.

        Args:
            queryset: Objects to be filtered.
            name: Name of the filter attribute, required by django-filter but
              unused, since this method only applies to the ``like`` filter.
            value: True to keep only the liked objects, False to exclude them.

        Returns:
            The objects liked by the user, or the ones that aren't liked.
        """
        liked = {"liked_by": self.request.user}
        return queryset.filter(Q(**liked) if value else ~Q(**liked)).all()


class MultipleFieldFilterSet(FilterSet):
    """Base filter set required to use the multiple field filters."""

    def multiple_field_filter(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        """Filter the objects matching the value in any of the configured fields.

        Args:
            queryset: Objects to be filtered.
            name: Name of the filter attribute on this filter set, used to look up
              its ``fields`` list in self.filters.
            value: Value to search for in all the configured fields.

        Returns:
            The objects matching the value in at least one of those fields.
        """
        query = Q()
        for field in self.filters[name].fields:
            query |= Q(**{field: value})
        return queryset.filter(query)


class MultipleFieldFilter(Filter):
    """Base filter that searches one value across several model fields.

    Only works within a MultipleFieldFilterSet, since that's the filter set that
    implements the filtering method configured here.

    Attributes:
        fields: Model fields, including related lookups, where the value is searched.
    """

    def __init__(self, fields: list[str], **kwargs: Any) -> None:
        """Prepare the filter with the fields where the value will be searched.

        Args:
            fields: Model fields, including related lookups, to search in.
            **kwargs: Standard filter arguments.
        """
        self.fields = fields
        # Method defined in MultipleFieldFilterSet
        kwargs["method"] = "multiple_field_filter"
        super().__init__(**kwargs)


class MultipleNumberFilter(MultipleFieldFilter, NumberFilter):
    """Multiple field filter for numeric values."""

    pass


class MultipleCharFilter(MultipleFieldFilter, CharFilter):
    """Multiple field filter for text values."""

    pass


class MultipleModelFilter(MultipleFieldFilter, ModelChoiceFilter):
    """Multiple field filter for references to another model."""

    pass

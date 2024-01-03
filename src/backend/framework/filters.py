from typing import Any, List

from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet, filters


class LikeFilter(FilterSet):
    """Filter that allows queryset filtering based on current user likes."""

    # Indicate if user likes or not the entities
    like = filters.BooleanFilter(method="get_liked_items")

    def get_liked_items(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Filter queryset based on current user likes.

        Args:
            queryset (QuerySet): Queryset to be filtered
            name (str): Field name. Not used in this case
            value (bool): Indicate if current user likes or not the entities

        Returns:
            QuerySet: Queryset filtered by the current user likes
        """
        liked = {"liked_by": self.request.user}
        return queryset.filter(Q(**liked) if value else ~Q(**liked)).all()


class MultipleFieldFilterSet(FilterSet):
    def multiple_field_filter(
        self, queryset: QuerySet, name: str, value: Any
    ) -> QuerySet:
        query = Q()
        for field in self.filters[name].fields:
            query |= Q(**{field: value})
        return queryset.filter(query)


class MultipleFieldFilter(filters.Filter):
    def __init__(self, fields: List[str], **kwargs: Any) -> None:
        kwargs["method"] = "multiple_field_filter"
        super().__init__(**kwargs)
        self.fields = fields


class MultipleNumberFilter(MultipleFieldFilter, filters.NumberFilter):
    pass


class MultipleCharFilter(MultipleFieldFilter, filters.CharFilter):
    pass


class MultipleModelChoiceFilter(MultipleFieldFilter, filters.ModelChoiceFilter):
    pass

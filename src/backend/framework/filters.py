from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import BooleanFilter, Filter, NumberFilter


class LikeFilter(FilterSet):
    # Indicate if user likes or not the entities
    like = BooleanFilter(method="get_liked_items")

    def get_liked_items(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        liked = {"liked_by": self.request.user}
        return queryset.filter(Q(**liked) if value else ~Q(**liked)).all()


class MultipleFieldFilterSet(FilterSet):
    def multiple_field_filter(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        query = Q()
        for field in self.filters[name].fields:
            query |= Q(**{field: value})
        return queryset.filter(query)


class MultipleFieldFilter(Filter):
    def __init__(self, fields: list[str], **kwargs: Any) -> None:
        self.fields = fields
        kwargs["method"] = "multiple_field_filter"
        super().__init__(**kwargs)


class MultipleNumberFilter(MultipleFieldFilter, NumberFilter):
    pass


class MultipleCharFilter(MultipleFieldFilter, CharFilter):
    pass

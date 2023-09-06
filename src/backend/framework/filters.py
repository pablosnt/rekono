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

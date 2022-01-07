from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters


class LikeFilter(FilterSet):
    liked = filters.BooleanFilter(method='get_liked_items')

    def get_liked_items(self, queryset, name, value):
        liked = {'liked_by': self.request.user}
        if value:
            liked = Q(**liked)
        else:
            liked = ~Q(**liked)
        return queryset.filter(liked).all()

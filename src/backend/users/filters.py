from django.db.models import QuerySet
from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from users.models import User


class UserFilter(FilterSet):
    # Get users that are members of this project
    project = NumberFilter(method="filter_project_members")
    # Get users that are NOT members of this project
    no_project = NumberFilter(method="filter_no_project_members")
    role = CharFilter(field_name="groups__name")

    class Meta:
        model = User
        fields = {
            "username": ["exact", "icontains"],
            "first_name": ["exact", "icontains"],
            "last_name": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "is_active": ["exact"],
            "date_joined": ["gte", "lte", "exact"],
            "groups": ["exact"],
        }

    def filter_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        return (
            queryset.filter(projects__id=value)
            if self.request.user.projects.filter(pk=value).exists()
            else queryset.none()
        )

    def filter_no_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        return (
            # queryset.exclude(id__in=User.objects.filter(projects__id=value).values_list("id", flat=True))
            # TODO: Test that the new version works
            queryset.exclude(projects__id=value)
            if self.request.user.projects.filter(pk=value).exists()
            else queryset.none()
        )

from django.db.models import QuerySet
from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from projects.models import Project
from users.models import User


class UserFilter(FilterSet):
    """FilterSet to filter and sort User entities."""

    project = NumberFilter(method="filter_project_members")
    # Get users that aren't members of this project
    no_project = NumberFilter(method="filter_no_project_members")
    role = CharFilter(field_name="groups__name")

    class Meta:
        """FilterSet metadata."""

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

    def _check_project_membership(self, id: int) -> bool:
        try:
            self.request.user.projects.get(pk=id)
            return True
        except Project.DoesNotExist:
            return False

    def filter_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        return queryset.filter(projects__id=value) if self._check_project_membership(value) else queryset.none()

    def filter_no_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        return (
            queryset.exclude(id__in=User.objects.filter(projects__id=value).values_list("id", flat=True))
            if self._check_project_membership(value)
            else queryset.none()
        )

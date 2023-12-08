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

    def _get_project_members(self, queryset: QuerySet, project_id: int) -> QuerySet:
        try:
            return (
                self.request.user.projects.get(pk=project_id)
                .members.filter(is_active=True)
                .order_by("-id")
            )
        except Project.DoesNotExist:
            return queryset.none()

    def filter_project_members(
        self, queryset: QuerySet, name: str, value: int
    ) -> QuerySet:
        return self._get_project_members(queryset, value)

    def filter_no_project_members(
        self, queryset: QuerySet, name: str, value: int
    ) -> QuerySet:
        project_members = self._get_project_members(queryset, value)
        return User.objects.exclude(id__in=project_members.values_list("id", flat=True))

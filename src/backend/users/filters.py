from django.db.models import QuerySet
from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from projects.models import Project
from users.models import User


class UserFilter(FilterSet):
    """FilterSet to filter and sort User entities."""

    project = NumberFilter(field_name="project", method="filter_project_members")
    # Get users that aren't members of these project
    no_project = NumberFilter(
        field_name="project", method="filter_project_members", exclude=True
    )
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

    def filter_project_members(
        self, queryset: QuerySet, name: str, value: int
    ) -> QuerySet:
        """Filter queryset, including only users that are members of a specific project.

        Args:
            queryset (QuerySet): User queryset to be filtered
            name (str): Field name, not used in this case
            value (int): Project Id

        Returns:
            QuerySet: Filtered queryset by project
        """
        try:
            return (
                self.request.user.projects.get(pk=value)
                .members.filter(is_active=True)
                .order_by("-id")
            )
        except Project.DoesNotExist:
            return queryset.none()

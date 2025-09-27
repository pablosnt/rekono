"""Django filters for user model queries.

Provides filtering capabilities for user queries including project membership
filtering and role-based filtering with proper access control.
"""

from django.db.models import QuerySet
from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from users.models import User


class UserFilter(FilterSet):
    """Filter class for User model queries.

    Provides filtering capabilities for user searches including project
    membership filtering and role-based queries with access control.

    Attributes:
        project (NumberFilter): Filter users who are members of specific project
        no_project (NumberFilter): Filter users who are NOT members of specific project
        role (CharFilter): Filter users by their assigned role
    """

    # Get users that are members of this project
    project = NumberFilter(method="filter_project_members")
    # Get users that are NOT members of this project
    no_project = NumberFilter(method="filter_no_project_members")
    role = CharFilter(field_name="groups__name")

    class Meta:
        """Meta configuration for the UserFilter.

        Attributes:
            model (Model): The User model to filter
            fields (dict): Field names mapped to allowed filter operations
        """

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
        """Filter users who are members of the specified project.

        Only returns results if the requesting user has access to the project.

        Args:
            queryset (QuerySet): Base queryset to filter
            name (str): Filter field name
            value (int): Project ID to filter by

        Returns:
            QuerySet: Filtered queryset of project members or empty if no access
        """
        return (
            queryset.filter(projects__id=value)
            if self.request.user.projects.filter(pk=value).exists()
            else queryset.none()
        )

    def filter_no_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """Filter users who are not members of the specified project.

        Only returns results if the requesting user has access to the project.

        Args:
            queryset (QuerySet): Base queryset to filter
            name (str): Filter field name
            value (int): Project ID to filter by

        Returns:
            QuerySet: Filtered queryset excluding project members or empty if no access
        """
        return (
            # queryset.exclude(id__in=User.objects.filter(projects__id=value).values_list("id", flat=True))
            # TODO: Test that the new version works
            queryset.exclude(projects__id=value)
            if self.request.user.projects.filter(pk=value).exists()
            else queryset.none()
        )

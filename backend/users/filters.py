"""Filters of the user endpoints."""

from django.db.models import QuerySet
from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from users.models import User


class UserFilter(FilterSet):
    """Filters to search users, including by their membership in a project.

    Attributes:
        project: Filter the members of a project.
        no_project: Filter the users that aren't members of a project, which is
          what the project members page needs to offer new members.
        role: Filter by the role of the users.
    """

    project = NumberFilter(method="filter_project_members")
    no_project = NumberFilter(method="filter_no_project_members")
    role = CharFilter(field_name="groups__name")

    class Meta:
        """Filter configuration for the users."""

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
        """Filter the members of a project.

        Args:
            queryset: Users to be filtered.
            name: Model field of the filter, not used, since the project is not
              reached through a single field.
            value: Identifier of the project, and not of a user.

        Returns:
            The members of the project, or no user at all when the user that
            performs the request isn't a member of it, so the members of a project
            are only known by the project itself.
        """
        return (
            queryset.filter(projects__id=value)
            if self.request.user.projects.filter(pk=value).exists()
            else queryset.none()
        )

    def filter_no_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """Filter the users that aren't members of a project.

        Args:
            queryset: Users to be filtered.
            name: Model field of the filter, not used, since the project is not
              reached through a single field.
            value: Identifier of the project, and not of a user.

        Returns:
            The users that aren't members of the project, or no user at all when the
            user that performs the request isn't a member of it.
        """
        return (
            queryset.exclude(projects__id=value)
            if self.request.user.projects.filter(pk=value).exists()
            else queryset.none()
        )

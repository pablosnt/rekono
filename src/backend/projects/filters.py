from django_filters.rest_framework import FilterSet
from projects.models import Project


class ProjectFilter(FilterSet):
    """FilterSet to filter Project entities."""

    class Meta:

        model = Project
        fields = {
            "name": ["exact", "icontains"],
            # "owner": ["exact"],
            # "owner__username": ["exact"],
            # "members": ["exact"],
            "tags__name": ["in"],
        }

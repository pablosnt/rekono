"""Filters of the authentication endpoints."""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from authentications.models import Authentication
from projects.models import Project
from targets.models import Target


class AuthenticationFilter(FilterSet):
    """Filters to search credentials by name, type, and where they are used.

    Attributes:
        target: Filter by the target that owns the port of the credential.
        project: Filter by the project that owns that target.
    """

    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="target_port__target")
    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name=("target_port__target__project"))

    class Meta:
        """Filter configuration for the credentials."""

        model = Authentication
        fields = {
            "target_port": ["exact", "isnull"],
            "name": ["exact", "icontains"],
            "type": ["exact"],
        }

"""Django REST framework filters for authentication models.

This module provides filtering capabilities for authentication records,
allowing users to filter authentication data by various criteria such
as target, project, target port, name, and type.
"""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from authentications.models import Authentication
from projects.models import Project
from targets.models import Target


class AuthenticationFilter(FilterSet):
    """Filter set for Authentication model.

    This class provides filtering capabilities for authentication records,
    allowing filtering by target, project, target port, name, and type.

    Attributes:
        target (ModelChoiceFilter): Filter by target associated with the
            authentication record.
        project (ModelChoiceFilter): Filter by project associated with the
            authentication record.
    """

    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="target_port__target")
    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name=("target_port__target__project"))

    class Meta:
        """Meta configuration for the AuthenticationFilter.

        Attributes:
            model: The Authentication model to filter.
            fields: Dictionary defining available filters and their lookup types.
        """

        model = Authentication
        fields = {
            "target_port": ["exact", "isnull"],
            "name": ["exact", "icontains"],
            "type": ["exact"],
        }

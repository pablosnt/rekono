"""Django REST framework filters for authentication models.

Provides filtering capabilities for authentication records by target,
project, target port, name, and authentication type.
"""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from authentications.models import Authentication
from projects.models import Project
from targets.models import Target


class AuthenticationFilter(FilterSet):
    """Filter set for Authentication model.

    Provides filtering capabilities for authentication records by various
    criteria including target, project, port, name, and type.

    Attributes:
        target (ModelChoiceFilter): Filter by associated target
        project (ModelChoiceFilter): Filter by associated project
    """

    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="target_port__target")
    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name=("target_port__target__project"))

    class Meta:
        """Meta configuration for the AuthenticationFilter.

        Attributes:
            model (Model): The Authentication model to filter
            fields (dict): Available filters and their lookup types
        """

        model = Authentication
        fields = {
            "target_port": ["exact", "isnull"],
            "name": ["exact", "icontains"],
            "type": ["exact"],
        }

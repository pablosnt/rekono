from authentications.models import Authentication
from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet
from projects.models import Project
from targets.models import Target


class AuthenticationFilter(FilterSet):
    """FilterSet to filter and sort authentications entities."""

    target = ModelChoiceFilter(
        queryset=Target.objects.all(), field_name="target_port__target"
    )
    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target_port__target__project"
    )

    class Meta:
        model = Authentication
        fields = {
            "target_port": ["exact", "isnull"],
            "name": ["exact", "icontains"],
            "type": ["exact"],
        }

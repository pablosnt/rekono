from authentications.models import Authentication
from django_filters.rest_framework import FilterSet


class AuthenticationFilter(FilterSet):
    """FilterSet to filter and sort authentications entities."""

    class Meta:
        model = Authentication
        fields = {
            "target_port": ["exact", "isnull"],
            "target_port__target": ["exact"],
            "target_port__target__project": ["exact"],
            "target_port__target__project__name": ["exact", "icontains"],
            "target_port__target__target": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            "type": ["exact"],
        }

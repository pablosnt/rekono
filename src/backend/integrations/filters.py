from integrations.models import Integration
from django_filters.rest_framework import FilterSet


class IntegrationFilter(FilterSet):
    class Meta:
        model = Integration
        fields = {"name": ["exact", "icontains"], "enabled": ["exact"]}

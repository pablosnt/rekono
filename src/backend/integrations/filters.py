from django_filters.rest_framework import FilterSet

from integrations.models import Integration


class IntegrationFilter(FilterSet):
    class Meta:
        model = Integration
        fields = {"name": ["exact", "icontains"], "enabled": ["exact"]}

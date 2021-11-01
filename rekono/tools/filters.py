from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from tools.models import Configuration, Tool


class ToolFilter(rest_framework.FilterSet):
    o = OrderingFilter(
        fields=('name', 'stage')
    )

    class Meta:
        model = Tool
        fields = {
            'name': ['exact', 'contains'],
            'command': ['exact', 'contains'],
            'stage': ['exact'],
        }


class ConfigurationFilter(rest_framework.FilterSet):
    o = OrderingFilter(
        fields=('tool', 'name')
    )

    class Meta:
        model = Configuration
        fields = {
            'tool': ['exact'],
            'tool__name': ['exact', 'contains'],
            'tool__command': ['exact', 'contains'],
            'tool__stage': ['exact'],
            'name': ['exact', 'contains'],
            'default': ['exact'],
        }

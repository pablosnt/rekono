from django_filters import rest_framework
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from tools.enums import FindingType
from tools.models import Configuration, Tool


class ToolFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('name', 'stage'))

    class Meta:
        model = Tool
        fields = {
            'name': ['exact', 'icontains'],
            'command': ['exact', 'icontains'],
            'configurations': ['exact'],
            'configurations__name': ['exact', 'icontains'],
            'configurations__inputs__type': ['exact'],
            'configurations__outputs__type': ['exact'],
            'stage': ['exact']
        }


class ConfigurationFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('tool', 'name'))

    class Meta:
        model = Configuration
        fields = {
            'tool': ['exact'],
            'tool__name': ['exact', 'icontains'],
            'tool__command': ['exact', 'icontains'],
            'tool__stage': ['exact'],
            'name': ['exact', 'icontains'],
            'default': ['exact'],
            'inputs__type': ['exact'],
            'outputs__type': ['exact'],
        }

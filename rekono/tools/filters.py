from django_filters.rest_framework import FilterSet, filters
from likes.filters import LikeFilter
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    o = filters.OrderingFilter(fields=('name', 'stage', 'likes_count'))

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


class ConfigurationFilter(FilterSet):
    o = filters.OrderingFilter(fields=('tool', 'name'))

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

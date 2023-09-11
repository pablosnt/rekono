from django_filters.rest_framework import FilterSet
from framework.filters import LikeFilter
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    class Meta:
        model = Tool
        fields = {
            "name": ["exact", "icontains"],
            "command": ["exact", "icontains"],
            "version": ["exact", "icontains"],
            "configurations": ["exact"],
            "configurations__name": ["exact", "icontains"],
            "configurations__stage": ["exact"],
            "intensities__value": ["exact"],
            "arguments__inputs__type__name": ["exact"],
            "configurations__outputs__type__name": ["exact"],
        }


class ConfigurationFilter(FilterSet):
    class Meta:
        model = Configuration
        fields = {
            "name": ["exact", "icontains"],
            "tool": ["exact"],
            "tool__name": ["exact", "icontains"],
            "tool__command": ["exact", "icontains"],
            "arguments": ["exact", "icontains"],
            "stage": ["exact"],
            "default": ["exact"],
            "tool__arguments__inputs__type__name": ["exact"],
            "outputs__type__name": ["exact"],
        }

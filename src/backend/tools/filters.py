from django_filters.filters import CharFilter, ChoiceFilter
from django_filters.rest_framework import FilterSet

from framework.filters import LikeFilter
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    stage = ChoiceFilter(field_name="configurations__stage")
    intensity = ChoiceFilter(field_name="intensities__value")
    input = CharFilter(field_name="arguments__inputs__type__name")
    output = CharFilter(field_name="configurations__outputs__type__name")

    class Meta:
        model = Tool
        fields = {
            "name": ["exact", "icontains"],
            "command": ["exact", "icontains"],
            "script": ["exact", "icontains"],
            "is_installed": ["exact"],
            "version": ["exact", "icontains"],
            "configurations": ["exact"],
        }


class ConfigurationFilter(FilterSet):
    input = CharFilter(field_name="tool__arguments__inputs__type__name")
    output = CharFilter(field_name="outputs__type__name")

    class Meta:
        model = Configuration
        fields = {
            "name": ["exact", "icontains"],
            "tool": ["exact"],
            "arguments": ["exact", "icontains"],
            "stage": ["exact"],
            "default": ["exact"],
        }

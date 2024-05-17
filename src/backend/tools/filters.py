from django.db.models import QuerySet
from django_filters.filters import CharFilter, ChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from framework.filters import LikeFilter
from tools.enums import Intensity, Stage
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    stage = ChoiceFilter(field_name="configurations__stage", choices=Stage.choices)
    intensity = ChoiceFilter(field_name="intensities__value", choices=Intensity.choices)
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
    output = CharFilter(field_name="outputs__type__name")
    process = NumberFilter(field_name="steps__process__id")
    no_process = NumberFilter(field_name="steps__process__id", exclude=True)

    class Meta:
        model = Configuration
        fields = {
            "name": ["exact", "icontains"],
            "tool": ["exact"],
            "arguments": ["exact", "icontains"],
            "stage": ["exact"],
            "default": ["exact"],
        }

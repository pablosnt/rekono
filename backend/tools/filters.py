"""Filters of the tool endpoints."""

from django_filters.filters import CharFilter, ChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from framework.filters import LikeFilter
from tools.enums import Intensity, Stage
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    """Filters to search the tools by what they can do.

    Attributes:
        stage: Filter by the phase where the configurations of the tool are run.
        intensity: Filter by an intensity that the tool supports.
        input: Filter by an input type that the tool accepts.
        output: Filter by a finding type that the tool discovers.
    """

    stage = ChoiceFilter(field_name="configurations__stage", choices=Stage.choices)
    intensity = ChoiceFilter(field_name="intensities__value", choices=Intensity.choices)
    input = CharFilter(field_name="configurations__arguments__inputs__type__name")
    output = CharFilter(field_name="configurations__outputs__type__name")

    class Meta:
        """Filter configuration for the tools."""

        model = Tool
        fields = {
            "name": ["exact", "icontains"],
            "command": ["exact", "icontains"],
            "script": ["exact", "icontains"],
            "is_installed": ["exact"],
            "version": ["exact", "icontains"],
            "configurations": ["exact"],
            "icon": ["isnull"],
        }


class ConfigurationFilter(FilterSet):
    """Filters to search the configurations by what they need and produce.

    Attributes:
        input: Filter by an input type that the configuration accepts.
        output: Filter by a finding type that the configuration discovers.
        process: Filter by a process that includes the configuration.
        no_process: Filter the configurations that a process doesn't include yet.
    """

    input = CharFilter(field_name="arguments__inputs__type__name")
    output = CharFilter(field_name="outputs__type__name")
    process = NumberFilter(field_name="steps__process__id")
    no_process = NumberFilter(field_name="steps__process__id", exclude=True)

    class Meta:
        """Filter configuration for the tool configurations."""

        model = Configuration
        fields = {
            "name": ["exact", "icontains"],
            "tool": ["exact"],
            "command_template": ["exact", "icontains"],
            "stage": ["exact"],
            "default": ["exact"],
        }

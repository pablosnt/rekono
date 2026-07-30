"""Django filter classes for tools and configurations API endpoints.

Provides filter sets for tools and configurations with support for complex
field filtering, relationship filtering, and specialized tool-related queries.
"""

from django_filters.filters import CharFilter, ChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from framework.filters import LikeFilter
from tools.enums import Intensity, Stage
from tools.models import Configuration, Tool


class ToolFilter(LikeFilter):
    """Filter set for Tool model with advanced filtering capabilities.

    Extends LikeFilter to provide comprehensive filtering options for tools
    including stage, intensity, input/output types, and standard field filters.
    Supports complex relationship filtering across tool configurations and arguments.

    Attributes:
        stage (ChoiceFilter): Exact match on Configuration.stage via
                              configurations__stage, restricted to Stage choices
        intensity (ChoiceFilter): Exact match on Intensity.value via
                                  intensities__value, restricted to Intensity choices
        input (CharFilter): Exact match on InputType.name via
                            configurations__arguments__inputs__type__name
        output (CharFilter): Exact match on InputType.name via
                             configurations__outputs__type__name
    """

    stage = ChoiceFilter(field_name="configurations__stage", choices=Stage.choices)
    intensity = ChoiceFilter(field_name="intensities__value", choices=Intensity.choices)
    input = CharFilter(field_name="configurations__arguments__inputs__type__name")
    output = CharFilter(field_name="configurations__outputs__type__name")

    class Meta:
        """Meta configuration for ToolFilter.

        Attributes:
            model (type): The Tool model to filter
            fields (dict): Field names and their allowed filter types
        """

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
    """Filter set for Configuration model with process and input/output filtering.

    Provides filtering capabilities for tool configurations including input/output types,
    process associations, and standard configuration field filtering.

    Attributes:
        input (CharFilter): Exact match on InputType.name via arguments__inputs__type__name
        output (CharFilter): Exact match on InputType.name via outputs__type__name
        process (NumberFilter): Exact match on Process.id via steps__process__id
        no_process (NumberFilter): Excludes configurations whose steps__process__id
                                    equals the given Process id (exclude=True)
    """

    input = CharFilter(field_name="arguments__inputs__type__name")
    output = CharFilter(field_name="outputs__type__name")
    process = NumberFilter(field_name="steps__process__id")
    no_process = NumberFilter(field_name="steps__process__id", exclude=True)

    class Meta:
        """Meta configuration for ConfigurationFilter.

        Attributes:
            model (type): The Configuration model to filter
            fields (dict): Field names and their allowed filter types
        """

        model = Configuration
        fields = {
            "name": ["exact", "icontains"],
            "tool": ["exact"],
            "command_template": ["exact", "icontains"],
            "stage": ["exact"],
            "default": ["exact"],
        }

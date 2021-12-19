from django_filters import rest_framework
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from tools.enums import FindingType
from tools.models import Configuration, Tool

from rekono.api.filters import BaseFilter


class ToolFilter(BaseFilter):
    o = OrderingFilter(fields=('name', 'stage'))
    configuration = filters.NumberFilter(
        field_name='configurations',
        method='related_field_filter'
    )
    configuration__name = filters.CharFilter(
        field_name='configurations__name',
        method='related_field_filter'
    )
    configuration__name__iexact = filters.CharFilter(
        field_name='configurations__name__iexact',
        method='related_field_filter'
    )
    configuration__name__contains = filters.CharFilter(
        field_name='configurations__name__contains',
        method='related_field_filter'
    )
    configuration__name__icontains = filters.CharFilter(
        field_name='configurations__name__icontains',
        method='related_field_filter'
    )
    input = filters.ChoiceFilter(
        field_name='configurations__inputs__type',
        method='related_field_filter',
        choices=FindingType.choices
    )
    output = filters.ChoiceFilter(
        field_name='configurations__outputs__type',
        method='related_field_filter',
        choices=FindingType.choices
    )

    class Meta:
        model = Tool
        fields = {
            'name': ['exact', 'iexact', 'contains', 'icontains'],
            'command': ['exact', 'iexact', 'contains', 'icontains'],
            'stage': ['exact']
        }


class ConfigurationFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('tool', 'name'))

    class Meta:
        model = Configuration
        fields = {
            'tool': ['exact'],
            'tool__name': ['exact', 'iexact', 'contains', 'icontains'],
            'tool__command': ['exact', 'iexact', 'contains', 'icontains'],
            'tool__stage': ['exact'],
            'name': ['exact', 'iexact', 'contains', 'icontains'],
            'default': ['exact'],
        }

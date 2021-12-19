from django_filters import rest_framework
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from processes.models import Process, Step

from rekono.api.filters import BaseFilter


class ProcessFilter(BaseFilter):
    o = OrderingFilter(fields=('name', 'creator'))
    tool = filters.NumberFilter(field_name='steps__tool', method='related_field_filter')
    tool__name = filters.CharFilter(field_name='steps__tool__name', method='related_field_filter')
    tool__name__iexact = filters.CharFilter(
        field_name='steps__tool__name__iexact',
        method='related_field_filter'
    )
    tool__name__contains = filters.CharFilter(
        field_name='steps__tool__name__contains',
        method='related_field_filter'
    )
    tool__name__icontains = filters.CharFilter(
        field_name='steps__tool__name__icontains',
        method='related_field_filter'
    )
    tool__stage = filters.NumberFilter(
        field_name='steps__tool__stage',
        method='related_field_filter'
    )

    class Meta:
        model = Process
        fields = {
            'name': ['exact', 'iexact', 'contains', 'icontains'],
            'description': ['exact', 'iexact', 'contains', 'icontains'],
            'creator': ['exact'],
            'creator__username': ['exact', 'iexact', 'contains', 'icontains']
        }


class StepFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('process', 'tool', 'configuration', 'priority'))

    class Meta:
        model = Step
        fields = {
            'process__name': ['exact', 'iexact', 'contains', 'icontains'],
            'process__description': ['exact', 'iexact', 'contains', 'icontains'],
            'process__creator': ['exact'],
            'tool': ['exact'],
            'tool__name': ['exact', 'iexact', 'contains', 'icontains'],
            'tool__command': ['exact', 'iexact', 'contains', 'icontains'],
            'tool__stage': ['exact'],
            'configuration': ['exact'],
            'configuration__name': ['exact', 'iexact', 'contains', 'icontains'],
            'priority': ['exact'],
        }

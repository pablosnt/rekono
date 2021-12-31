from django_filters import rest_framework
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from processes.models import Process, Step


class ProcessFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('name', 'creator'))

    class Meta:
        model = Process
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'creator': ['exact'],
            'creator__username': ['exact', 'icontains'],
            'steps__tool': ['exact'],
            'steps__tool__name': ['exact', 'icontains'],
            'steps__tool__stage': ['exact'],
            'steps__configuration': ['exact'],
            'steps__configuration__name': ['exact', 'icontains']
        }


class StepFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('process', 'tool', 'configuration', 'priority'))

    class Meta:
        model = Step
        fields = {
            'process__name': ['exact', 'icontains'],
            'process__description': ['exact', 'icontains'],
            'process__creator': ['exact'],
            'tool': ['exact'],
            'tool__name': ['exact', 'icontains'],
            'tool__command': ['exact', 'icontains'],
            'tool__stage': ['exact'],
            'configuration': ['exact'],
            'configuration__name': ['exact', 'icontains'],
            'priority': ['exact'],
        }

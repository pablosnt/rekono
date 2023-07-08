from django_filters.rest_framework import FilterSet, filters
from likes.filters import LikeFilter

from processes.models import Process, Step


class ProcessFilter(LikeFilter):
    '''FilterSet to filter and sort Process entities.'''

    o = filters.OrderingFilter(fields=('name', 'creator', 'likes_count'))       # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Process
        fields = {                                                              # Filter fields
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'creator': ['exact'],
            'creator__username': ['exact', 'icontains'],
            'steps__tool': ['exact'],
            'steps__tool__name': ['exact', 'icontains'],
            'steps__configuration': ['exact'],
            'steps__configuration__name': ['exact', 'icontains'],
            'steps__configuration__stage': ['exact'],
            'tags__name': ['in'],
        }


class StepFilter(FilterSet):
    '''FilterSet to filter and sort Step entities.'''

    o = filters.OrderingFilter(fields=('process', 'tool', 'configuration', 'priority'))             # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Step
        fields = {                                                              # Filter fields
            'process__name': ['exact', 'icontains'],
            'process__description': ['exact', 'icontains'],
            'process__creator': ['exact'],
            'tool': ['exact'],
            'tool__name': ['exact', 'icontains'],
            'tool__command': ['exact', 'icontains'],
            'configuration': ['exact'],
            'configuration__name': ['exact', 'icontains'],
            'configuration__stage': ['exact'],
            'priority': ['exact'],
        }

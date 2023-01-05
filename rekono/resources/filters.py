from django_filters.rest_framework import filters
from likes.filters import LikeFilter

from resources.models import Wordlist


class WordlistFilter(LikeFilter):
    '''FilterSet to filter and sort Wordlist entities.'''

    o = filters.OrderingFilter(fields=('name', 'type', 'creator', 'likes_count'))                   # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Wordlist
        fields = {                                                              # Filter fields
            'name': ['exact', 'icontains'],
            'type': ['exact'],
            'creator': ['exact'],
            'creator__username': ['exact', 'icontains'],
            'size': ['gte', 'lte', 'exact'],
        }

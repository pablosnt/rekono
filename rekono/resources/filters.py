from django_filters.rest_framework import filters
from likes.filters import LikeFilter
from resources.models import Wordlist


class WordlistFilter(LikeFilter):
    o = filters.OrderingFilter(fields=('name', 'type', 'creator', 'likes_count'))

    class Meta:
        model = Wordlist
        fields = {
            'name': ['exact', 'icontains'],
            'type': ['exact'],
            'creator': ['exact'],
            'creator__username': ['exact', 'icontains'],
            'size': ['gte', 'lte', 'exact'],
        }

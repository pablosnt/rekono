# from likes.filters import LikeFilter
from django_filters.rest_framework import FilterSet
from wordlists.models import Wordlist


class WordlistFilter(FilterSet):
    """FilterSet to filter and sort Wordlist entities."""

    class Meta:
        model = Wordlist
        fields = {  # Filter fields
            "name": ["exact", "icontains"],
            "type": ["exact"],
            # 'creator': ['exact'],
            # 'creator__username': ['exact', 'icontains'],
            "size": ["gte", "lte", "exact"],
        }

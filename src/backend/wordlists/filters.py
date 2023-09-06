from framework.filters import LikeFilter
from wordlists.models import Wordlist


class WordlistFilter(LikeFilter):
    """FilterSet to filter and sort Wordlist entities."""

    class Meta:
        model = Wordlist
        fields = {  # Filter fields
            "name": ["exact", "icontains"],
            "type": ["exact"],
            "owner": ["exact"],
            "owner__username": ["exact", "icontains"],
            "size": ["gte", "lte", "exact"],
        }

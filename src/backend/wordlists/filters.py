from framework.filters import LikeFilter
from wordlists.models import Wordlist


class WordlistFilter(LikeFilter):
    """FilterSet to filter and sort Wordlist entities."""

    class Meta:
        model = Wordlist
        fields = {
            "name": ["exact", "icontains"],
            "type": ["exact"],
            "owner": ["exact"],
            "size": ["gte", "lte", "exact"],
        }

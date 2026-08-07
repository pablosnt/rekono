"""Filters of the wordlist endpoints."""

from framework.filters import LikeFilter
from wordlists.models import Wordlist


class WordlistFilter(LikeFilter):
    """Filters to search the wordlists that the tools can use."""

    class Meta:
        """Filter configuration for the wordlists."""

        model = Wordlist
        fields = {
            "name": ["exact", "icontains"],
            "type": ["exact"],
            "owner": ["exact"],
            "size": ["gte", "lte", "exact"],
        }

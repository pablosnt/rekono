"""Django filter classes for wordlist model queries.

Provides filtering capabilities for wordlist API endpoints with support for
name, type, owner, and size-based filtering operations.
"""

from framework.filters import LikeFilter
from wordlists.models import Wordlist


class WordlistFilter(LikeFilter):
    """Filter class for Wordlist model queries.

    Extends LikeFilter to provide comprehensive filtering options for wordlist
    queries including text search, type filtering, ownership, and size ranges.
    """

    class Meta:
        """Meta configuration for WordlistFilter.

        Attributes:
            model (Model): The Wordlist model to filter
            fields (dict): Available filter fields and their lookup types
        """

        model = Wordlist
        fields = {
            "name": ["exact", "icontains"],
            "type": ["exact"],
            "owner": ["exact"],
            "size": ["gte", "lte", "exact"],
        }

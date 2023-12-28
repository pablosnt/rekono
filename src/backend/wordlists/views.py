from framework.views import LikeViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from security.authorization.permissions import (OwnerPermission,
                                                RekonoModelPermission)
from wordlists.filters import WordlistFilter
from wordlists.models import Wordlist
from wordlists.serializers import UpdateWordlistSerializer, WordlistSerializer

# Create your views here.


class WordlistViewSet(LikeViewSet):
    """Wordlist ViewSet that includes: get, retrieve, create, update, delete, like and dislike features."""

    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "type", "creator", "likes_count"]

    def get_serializer_class(self) -> Serializer:
        """Get serializer class to use in each request.

        Returns:
            Serializer: Properly serializer to use,
        """
        if self.request.method == "PUT":  # If PUT request method
            # Use specific serializer for wordlist update
            return UpdateWordlistSerializer
        return super().get_serializer_class()  # Otherwise, standard serializer

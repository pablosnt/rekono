"""Viewsets of the wordlist endpoints."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import LikeViewSet
from security.authorization.permissions import OwnerPermission, RekonoModelPermission
from wordlists.filters import WordlistFilter
from wordlists.models import Wordlist
from wordlists.serializers import UpdateWordlistSerializer, WordlistSerializer


class WordlistViewSet(LikeViewSet):
    """Manage the wordlists that the tools can use.

    Attributes:
        queryset: All the wordlists, since they are shared by all the projects.
        serializer_class: Serializer of the wordlists.
        filterset_class: Filters of the wordlists.
        permission_classes: Role permissions plus the ownership of the wordlist,
          so only its owner can update or remove it.
        search_fields: Free text search over the wordlist name.
        ordering_fields: Fields that the wordlists can be sorted by.
    """

    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "size", "type", "owner", "liked", "likes"]

    def get_serializer_class(self) -> Serializer:
        """Get the serializer without the file field for the update requests.

        Returns:
            The update serializer for PUT, so the file of an existing wordlist can't
            be replaced, and the standard one for the rest of the methods.
        """
        return UpdateWordlistSerializer if self.request.method == "PUT" else super().get_serializer_class()

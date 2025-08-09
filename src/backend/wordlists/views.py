from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import LikeViewSet
from security.authorization.permissions import OwnerPermission, RekonoModelPermission
from wordlists.filters import WordlistFilter
from wordlists.models import Wordlist
from wordlists.serializers import UpdateWordlistSerializer, WordlistSerializer


class WordlistViewSet(LikeViewSet):
    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "size", "type", "creator", "likes_count"]

    def get_serializer_class(self) -> Serializer:
        return UpdateWordlistSerializer if self.request.method == "PUT" else super().get_serializer_class()

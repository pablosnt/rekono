# from api.views import CreateWithUserViewSet
# from likes.views import LikeManagementView
# from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from framework.views import BaseViewSet

# from security.authorization.permissions import WordlistCreatorPermission

from wordlists.filters import WordlistFilter
from wordlists.models import Wordlist
from wordlists.serializers import UpdateWordlistSerializer, WordlistSerializer


# Create your views here.


class WordlistViewSet(BaseViewSet):
    """Wordlist ViewSet that includes: get, retrieve, create, update, delete, like and dislike features."""

    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    search_fields = ["name"]  # Fields used to search projects
    ordering_fields = ["id", "name", "type"]  # , 'creator', 'likes_count'
    # Required to include the WordlistCreatorPermission and remove unneeded ProjectMemberPermission
    # permission_classes = [
    #     IsAuthenticated,
    #     DjangoModelPermissions,
    #     WordlistCreatorPermission,
    # ]
    # user_field = "creator"

    def get_serializer_class(self) -> Serializer:
        """Get serializer class to use in each request.

        Returns:
            Serializer: Properly serializer to use,
        """
        if self.request.method == "PUT":  # If PUT request method
            # Use specific serializer for wordlist update
            return UpdateWordlistSerializer
        return super().get_serializer_class()  # Otherwise, standard serializer

"""Django REST framework views for wordlist management.

Provides REST API views for wordlist records with CRUD operations, file upload
capabilities, and proper authentication and authorization controls.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import LikeViewSet
from security.authorization.permissions import OwnerPermission, RekonoModelPermission
from wordlists.filters import WordlistFilter
from wordlists.models import Wordlist
from wordlists.serializers import UpdateWordlistSerializer, WordlistSerializer


class WordlistViewSet(LikeViewSet):
    """ViewSet for Wordlist model CRUD operations.

    Provides REST API endpoints for managing wordlist files with filtering, searching,
    ordering, and like functionality. Enforces owner-based authorization and user
    authentication for secure wordlist management.

    Attributes:
        queryset (QuerySet): Wordlist model instances
        serializer_class (Serializer): Serializer for Wordlist model
        filterset_class (FilterSet): Filter class for query filtering
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
    """

    queryset = Wordlist.objects.all()
    serializer_class = WordlistSerializer
    filterset_class = WordlistFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "size", "type", "owner", "likes_count"]

    def get_serializer_class(self) -> Serializer:
        """Get the appropriate serializer class based on the request method.

        Returns:
            Serializer: UpdateWordlistSerializer for PUT requests, WordlistSerializer otherwise
        """
        return UpdateWordlistSerializer if self.request.method == "PUT" else super().get_serializer_class()

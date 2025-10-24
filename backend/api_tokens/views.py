"""Views for managing API tokens via REST API endpoints.

Provides REST API endpoints for API token CRUD operations with user-scoped
access and proper authentication controls.
"""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from api_tokens.filters import ApiTokenFilter
from api_tokens.models import ApiToken
from api_tokens.serializers import ApiTokenSerializer, CreateApiTokenSerializer
from framework.views import BaseViewSet

# Create your views here.


class ApiTokenViewSet(BaseViewSet):
    """ViewSet for managing API tokens for the authenticated user.

    Provides GET, POST, and DELETE operations for user-owned API tokens
    with filtering, searching, and ordering capabilities.

    Attributes:
        queryset (QuerySet): All ApiToken objects
        serializer_class (Serializer): Default serializer for API tokens
        filterset_class (FilterSet): Filter class for token queries
        permission_classes (list): Required permissions for access
        authentication_classes (list): Authentication classes for request validation
        http_method_names (list): Allowed HTTP methods
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        owner_field (str): Field used for ownership filtering
    """

    queryset = ApiToken.objects.all()
    serializer_class = ApiTokenSerializer
    filterset_class = ApiTokenFilter
    permission_classes = [IsAuthenticated]
    # Needed to disallow API token management by an user authenticated with an API token
    authentication_classes = [JWTAuthentication]
    http_method_names = ["get", "post", "delete"]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "expiration"]
    owner_field = "user"

    def get_queryset(self) -> QuerySet:
        """Return queryset filtered to API tokens owned by the current user.

        Returns:
            QuerySet: API tokens filtered to the authenticated user
        """
        return super().get_queryset().filter(user=self.request.user).all()

    def get_serializer_class(self) -> Serializer:
        """Return the serializer class based on the request method.

        Returns:
            Serializer: CreateApiTokenSerializer for POST, ApiTokenSerializer otherwise
        """
        return CreateApiTokenSerializer if self.request.method == "POST" else super().get_serializer_class()

"""Views for managing API tokens via REST API endpoints."""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from api_tokens.filters import ApiTokenFilter
from api_tokens.models import ApiToken
from api_tokens.serializers import ApiTokenSerializer, CreateApiTokenSerializer
from framework.views import BaseViewSet

# Create your views here.


class ApiTokenViewSet(BaseViewSet):
    """ViewSet for listing, creating, and deleting API tokens for the authenticated user."""

    queryset = ApiToken.objects.all()
    serializer_class = ApiTokenSerializer
    filterset_class = ApiTokenFilter
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "expiration"]
    owner_field = "user"

    def get_queryset(self) -> QuerySet:
        """Return queryset filtered to API tokens owned by the current user.

        Returns:
            QuerySet: The filtered queryset for the current user.
        """
        return super().get_queryset().filter(user=self.request.user).all()

    def get_serializer_class(self) -> Serializer:
        """Return the serializer class based on the request method.

        Returns:
            Serializer: The serializer class to use.
        """
        return CreateApiTokenSerializer if self.request.method == "POST" else super().get_serializer_class()

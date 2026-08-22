"""Endpoints to manage the API tokens of the user that performs the request."""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from api_tokens.filters import ApiTokenFilter
from api_tokens.models import ApiToken
from api_tokens.serializers import ApiTokenSerializer, CreateApiTokenSerializer
from framework.views import BaseViewSet
from security.authentication.jwt import CookieJWTAuthentication


class ApiTokenViewSet(BaseViewSet):
    """Create, list, and delete the API tokens of a user.

    Attributes:
        queryset: All the API tokens, restricted to the ones of the user by
          get_queryset.
        serializer_class: Serializer that never exposes the token value.
        filterset_class: Filters available to search API tokens.
        permission_classes: Only authentication is required, since any user manages
          their own tokens.
        authentication_classes: Only the JWT authentication, so a user authenticated
          with an API token can't manage the API tokens.
        http_method_names: The tokens can be created and deleted, but not updated.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        owner_field: Field that references the user that owns each token.
    """

    queryset = ApiToken.objects.all()
    serializer_class = ApiTokenSerializer
    filterset_class = ApiTokenFilter
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    http_method_names = ["get", "post", "delete"]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "expiration"]
    owner_field = "user"

    def get_queryset(self) -> QuerySet:
        """Get the API tokens of the user that performs the request.

        Returns:
            Only their own tokens, since a token is personal and is never shared
            with the rest of the users.
        """
        return super().get_queryset().filter(user=self.request.user).all()

    def get_serializer_class(self) -> Serializer:
        """Get the serializer that returns the token value only when it's created.

        Returns:
            The creation serializer for POST, which is the only moment when the
            plain token is available, and the standard one otherwise.
        """
        return CreateApiTokenSerializer if self.request.method == "POST" else super().get_serializer_class()

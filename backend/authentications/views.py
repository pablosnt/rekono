"""Endpoints to manage the credentials of the target services."""

from rest_framework.permissions import IsAuthenticated

from authentications.filters import AuthenticationFilter
from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer
from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class AuthenticationViewSet(BaseViewSet):
    """Create, list, and delete the credentials of the target ports.

    Attributes:
        queryset: All the credentials, restricted to the projects of the user by
          the base viewset.
        serializer_class: Serializer that keeps the secret masked.
        filterset_class: Filters available to search credentials.
        permission_classes: Role permissions plus the membership in the project.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: The credentials can be created and deleted, but not
          updated, since a new secret means a new credential.
    """

    queryset = Authentication.objects.all()
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "type"]
    http_method_names = ["get", "post", "delete"]

"""HTTP Headers API views for security testing configuration management.

Provides RESTful API endpoints for managing HTTP headers used in security
testing operations with proper access control and data isolation.
"""

from django.db.models import Q, QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import BaseViewSet
from http_headers.filters import HttpHeaderFilter
from http_headers.models import HttpHeader
from http_headers.serializers import HttpHeaderSerializer, UpdateHttpHeaderSerializer
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class HttpHeaderViewSet(BaseViewSet):
    """ViewSet for HTTP header management with multi-scope access control.

    Provides complete CRUD operations for HTTP headers used in security testing
    with proper isolation between global, user-specific, and target-specific
    headers. Ensures users can only access their own headers or headers from
    projects they are members of.

    Attributes:
        queryset (QuerySet): Base queryset for all HTTP headers
        serializer_class (Serializer): Primary serializer for HTTP header data
        filterset_class (FilterSet): Filter class for header querying
        permission_classes (list): Required permissions for API access
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods for the viewset
    """

    queryset = HttpHeader.objects.all()
    serializer_class = HttpHeaderSerializer
    filterset_class = HttpHeaderFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = ["key", "value"]
    ordering_fields = ["id", "target", "user", "key", "value"]
    http_method_names = ["get", "put", "post", "delete"]

    def get_queryset(self) -> QuerySet:
        """Get filtered queryset with proper access control.

        Combines two conditions with AND: the header must belong to the
        current user or have no assigned user, and it must belong to a
        target from a project the current user is a member of or have no
        assigned target. This keeps fully global headers visible to
        everyone while restricting user-specific and target-specific
        headers to their owners and project members.

        Returns:
            QuerySet: Filtered queryset of accessible HTTP headers.
        """
        return self.queryset.filter(Q(user=self.request.user) | Q(user__isnull=True)).filter(
            Q(target__project__members=self.request.user) | Q(target__isnull=True)
        )

    def get_serializer_class(self) -> Serializer:
        """Get the appropriate serializer class based on the request method.

        Returns:
            Serializer: UpdateHttpHeaderSerializer for PUT requests, HttpHeaderSerializer otherwise
        """
        return UpdateHttpHeaderSerializer if self.request.method == "PUT" else super().get_serializer_class()

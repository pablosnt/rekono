"""Viewsets of the HTTP header endpoints."""

from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import BaseViewSet
from http_headers.filters import HttpHeaderFilter
from http_headers.models import HttpHeader
from http_headers.serializers import HttpHeaderSerializer, UpdateHttpHeaderSerializer
from security.authorization.permissions import (
    IsAdmin,
    ProjectMemberPermission,
    RekonoModelPermission,
)


class HttpHeaderViewSet(BaseViewSet):
    """Manage the HTTP headers that the tools send.

    Attributes:
        queryset: All the headers, filtered later by the scope of each one.
        serializer_class: Serializer of the HTTP headers.
        filterset_class: Filters of the HTTP headers.
        permission_classes: Role permissions plus the membership in the project of
          the target, if the header belongs to one.
        search_fields: Free text search over the header key and value.
        ordering_fields: Fields that the headers can be sorted by.
        http_method_names: All the methods except PATCH, since the headers are
          always updated with all their data.
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
        """Get the headers that apply to the user, to their projects, or to everybody.

        Returns:
            The headers of the user and the global ones, scoped to the targets of
            the projects where the user is a member.
        """
        return self.queryset.filter(Q(user=self.request.user) | Q(user__isnull=True)).filter(
            Q(target__project__members=self.request.user) | Q(target__isnull=True)
        )

    def get_serializer_class(self) -> Serializer:
        """Get the serializer without the scope fields for the update requests.

        Returns:
            The update serializer for PUT, so the scope of an existing header
            can't be changed, and the standard one for the rest of the methods.
        """
        return UpdateHttpHeaderSerializer if self.request.method == "PUT" else super().get_serializer_class()

    def perform_destroy(self, instance: HttpHeader) -> None:
        """Remove an HTTP header.

        Args:
            instance: Header to remove, whose scope decides who can do it.

        Raises:
            PermissionDenied: If the header belongs to another user, or if it's a
              global header and the user isn't an admin.
        """
        # The deletions don't go through any serializer, so the scope checks that the serializers
        # apply on creation and update are repeated here
        if (instance.user is not None and instance.user != self.request.user) or (
            instance.user is None and instance.target is None and not IsAdmin().has_permission(self.request, self)
        ):
            raise PermissionDenied()
        super().perform_destroy(instance)

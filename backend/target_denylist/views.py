"""Endpoints to manage the target denylist."""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import RekonoModelPermission
from target_denylist.filters import TargetDenylistFilter
from target_denylist.models import TargetDenylist
from target_denylist.serializers import TargetDenylistSerializer


class TargetDenylistViewSet(BaseViewSet):
    """Manage the denylist entries, which only the administrators can see.

    Attributes:
        queryset: All the denylist entries, since they aren't scoped to a project.
        filterset_class: Filters available to search denylist entries.
        serializer_class: Serializer of the denylist entries.
        permission_classes: Role permissions, which only grant access to the
          administrators.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: Standard CRUD methods.
    """

    queryset = TargetDenylist.objects.all()
    filterset_class = TargetDenylistFilter
    serializer_class = TargetDenylistSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["target"]
    ordering_fields = ["id", "target", "default", "blocked"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        """Get the denylist entries, hiding the default ones from the write methods.

        The entries provided by Rekono protect the platform itself, so they can be
        read but never updated or removed.

        Returns:
            All the entries, or only the ones created by the users for the write
            methods.
        """
        default_queryset = super().get_queryset()
        return (
            default_queryset.filter(default=False).all()
            if self.request.method in ["PUT", "DELETE"]
            else default_queryset
        )

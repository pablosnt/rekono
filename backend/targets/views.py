"""Endpoints to manage the targets of the projects."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import ProjectMemberPermission, RekonoModelPermission
from targets.filters import TargetFilter
from targets.models import Target
from targets.serializers import TargetSerializer


class TargetViewSet(BaseViewSet):
    """Create, list, and delete the targets of the projects.

    Attributes:
        queryset: All the targets, restricted to the projects of the user by the
          base viewset.
        serializer_class: Serializer of the targets.
        filterset_class: Filters available to search targets.
        permission_classes: Role permissions plus the membership in the project.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: The targets can be created and deleted, but not updated,
          since another value is another target.
    """

    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["target"]
    ordering_fields = ["id", "target", "type"]
    http_method_names = ["get", "post", "delete"]

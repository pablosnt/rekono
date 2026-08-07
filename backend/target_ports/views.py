"""Endpoints to manage the ports of the targets."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)
from target_ports.filters import TargetPortFilter
from target_ports.models import TargetPort
from target_ports.serializers import TargetPortSerializer


class TargetPortViewSet(BaseViewSet):
    """Create, list, and delete the ports of the targets.

    Attributes:
        queryset: All the target ports, restricted to the projects of the user by
          the base viewset.
        serializer_class: Serializer of the target ports.
        filterset_class: Filters available to search target ports.
        permission_classes: Role permissions plus the membership in the project.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: The target ports can be created and deleted, but not
          updated, since another port is another target port.
    """

    queryset = TargetPort.objects.all()
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    search_fields = ["port", "path"]
    ordering_fields = ["id", "target", "port", "path"]
    http_method_names = ["get", "post", "delete"]

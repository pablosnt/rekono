"""Endpoints to manage the processes and their steps."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet, LikeViewSet
from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import ProcessSerializer, StepSerializer
from security.authorization.permissions import OwnerPermission, RekonoModelPermission


class ProcessViewSet(LikeViewSet):
    """Manage the processes and like them.

    Attributes:
        queryset: All the processes, since they are shared by all the projects.
        serializer_class: Serializer of the processes.
        filterset_class: Filters available to search processes.
        permission_classes: Role permissions plus the ownership, so a user can only
          modify the processes that they created.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: Standard CRUD methods.
    """

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "owner", "liked", "likes"]
    http_method_names = ["get", "post", "put", "delete"]


class StepViewSet(BaseViewSet):
    """Add and remove the steps of a process.

    Attributes:
        queryset: Steps whose configuration can still be executed, since the
          deprecated ones are only kept for the historical executions.
        serializer_class: Serializer of the steps.
        filterset_class: Filters available to search steps.
        permission_classes: Role permissions plus the ownership of the process that
          contains the step.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: The steps can be created and deleted, but not updated,
          since another configuration is another step.
    """

    queryset = Step.objects.filter(configuration__deprecated=False)
    serializer_class = StepSerializer
    filterset_class = StepFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = [
        "process__name",
        "configuration__tool__name",
        "configuration__tool__command",
        "configuration__name",
    ]
    ordering_fields = ["id", "process", "configuration"]
    http_method_names = ["get", "post", "delete"]

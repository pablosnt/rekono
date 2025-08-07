"""Django REST framework views for process management operations.

Provides REST API endpoints for managing security testing processes and steps
with CRUD operations, filtering, search capabilities, and community features
through the like system for process sharing and discovery.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet, LikeViewSet
from processes.filters import ProcessFilter, StepFilter
from processes.models import Process, Step
from processes.serializers import ProcessSerializer, StepSerializer
from security.authorization.permissions import OwnerPermission, RekonoModelPermission


class ProcessViewSet(LikeViewSet):
    """ViewSet for managing security testing process workflows.

    Provides REST API endpoints for process CRUD operations with community
    features including like system for process rating and discovery.
    Supports filtering by tool configurations, stages, and tags.

    Attributes:
        queryset (QuerySet): All Process objects
        serializer_class (Serializer): ProcessSerializer for process operations
        filterset_class (FilterSet): ProcessFilter for querying processes
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST, PUT, DELETE)
    """

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    filterset_class = ProcessFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "owner", "likes_count"]
    http_method_names = ["get", "post", "put", "delete"]


class StepViewSet(BaseViewSet):
    """ViewSet for managing process workflow steps.

    Provides REST API endpoints for step CRUD operations within security
    testing processes. Enables creation and deletion of individual steps
    with filtering and search capabilities across process and tool configurations.

    Attributes:
        queryset (QuerySet): All Step objects
        serializer_class (Serializer): StepSerializer for step operations
        filterset_class (FilterSet): StepFilter for querying steps
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods (GET, POST, DELETE)
    """

    queryset = Step.objects.all()
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

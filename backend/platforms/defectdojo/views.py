"""Django REST framework views for DefectDojo integration management.

Provides REST API endpoints for DefectDojo configuration, project synchronization,
and entity management with proper authentication and authorization controls.
Supports DefectDojo settings management and external entity creation.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from framework.views import BaseViewSet
from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync
from platforms.defectdojo.serializers import (
    DefectDojoEngagementSerializer,
    DefectDojoProductSerializer,
    DefectDojoProductTypeSerializer,
    DefectDojoSettingsSerializer,
    DefectDojoSyncSerializer,
)
from security.authorization.permissions import (
    IsAuditor,
    ProjectMemberPermission,
    RekonoModelPermission,
)


class DefectDojoSettingsViewSet(BaseViewSet):
    """ViewSet for DefectDojo integration settings management.

    Provides REST API endpoints for viewing and updating DefectDojo integration
    configuration settings with proper authentication and authorization controls.
    Restricts access to authenticated users with appropriate permissions.

    Attributes:
        queryset (QuerySet): DefectDojoSettings model instances
        serializer_class (Serializer): Serializer for DefectDojo settings
        permission_classes (list): Required permissions for access control
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = DefectDojoSettings.objects.all()
    serializer_class = DefectDojoSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]


class DefectDojoSyncViewSet(BaseViewSet):
    """ViewSet for DefectDojo project synchronization management.

    Provides REST API endpoints for creating and deleting DefectDojo project
    synchronization mappings with project-level access control. Enables users
    to establish connections between Rekono projects and DefectDojo entities.

    Attributes:
        queryset (QuerySet): DefectDojoSync model instances
        serializer_class (Serializer): Serializer for DefectDojo synchronization
        permission_classes (list): Required permissions including project membership
        http_method_names (list): Allowed HTTP methods (POST, DELETE only)
    """

    queryset = DefectDojoSync.objects.all()
    serializer_class = DefectDojoSyncSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    http_method_names = ["post", "delete"]


class DefectDojoEntityViewSet(BaseViewSet):
    """Base ViewSet for creating DefectDojo entities via API integration.

    Provides common functionality for creating DefectDojo entities (product types,
    products, engagements) through direct API calls to DefectDojo instance.
    Restricts access to authenticated auditors with appropriate permissions.

    Attributes:
        http_method_names (list): Allowed HTTP methods (POST only)
        permission_classes (list): Required permissions for entity creation
    """

    http_method_names = ["post"]
    permission_classes = [IsAuthenticated, IsAuditor]

    def create(self, request: Request) -> Response:
        """Create a new DefectDojo entity through API integration.

        Validates request data and creates the corresponding entity in DefectDojo
        through the integration client. Returns the created entity ID on success
        or error message on failure.

        Args:
            request (Request): HTTP request containing entity creation data

        Returns:
            Response: HTTP 201 with entity ID on success, HTTP 400 on failure
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            response = serializer.create(serializer.validated_data)
            return Response({"id": response.get("id")}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({"defectdojo": "Error creating instance on DefectDojo"}, status=status.HTTP_400_BAD_REQUEST)


class DefectDojoProductTypeViewSet(DefectDojoEntityViewSet):
    """ViewSet for creating DefectDojo product types.

    Provides REST API endpoint for creating new product types in DefectDojo
    through direct API integration. Product types serve as the top-level
    organizational structure in DefectDojo's hierarchy.

    Attributes:
        serializer_class (Serializer): Serializer for DefectDojo product type creation
    """

    serializer_class = DefectDojoProductTypeSerializer


class DefectDojoProductViewSet(DefectDojoEntityViewSet):
    """ViewSet for creating DefectDojo products.

    Provides REST API endpoint for creating new products in DefectDojo
    through direct API integration. Products are associated with product
    types and represent specific applications or systems being tested.

    Attributes:
        serializer_class (Serializer): Serializer for DefectDojo product creation
    """

    serializer_class = DefectDojoProductSerializer


class DefectDojoEngagementViewSet(DefectDojoEntityViewSet):
    """ViewSet for creating DefectDojo engagements.

    Provides REST API endpoint for creating new engagements in DefectDojo
    through direct API integration. Engagements represent specific security
    assessments or testing periods within a product.

    Attributes:
        serializer_class (Serializer): Serializer for DefectDojo engagement creation
    """

    serializer_class = DefectDojoEngagementSerializer

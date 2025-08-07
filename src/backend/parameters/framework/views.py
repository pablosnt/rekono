"""Django REST framework base views for input parameters.

Provides base ViewSet implementation for input parameter management
with project-level access control and permission enforcement.
"""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class InputParameterViewSet(BaseViewSet):
    """Base ViewSet for input parameter management with project-level access control.

    Provides common functionality for all input parameter ViewSets including
    project-level filtering and permission enforcement through task associations.

    Attributes:
        queryset (QuerySet): Base queryset (overridden by concrete implementations)
        permission_classes (list): Required permissions for access
        http_method_names (list): Allowed HTTP methods (GET, POST only)
    """

    queryset = None
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    http_method_names = ["get", "post"]

    def get_queryset(self) -> QuerySet:
        """Filter queryset to show only parameters accessible to the current user.

        Filters parameters based on project membership through task associations,
        ensuring users only see parameters from projects they belong to.

        Returns:
            QuerySet: Filtered queryset of accessible input parameters
        """
        return self.queryset.filter(**{f"{self.linked_model._project_field}__members": self.request.user}).distinct()

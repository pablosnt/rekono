"""Base viewset of the input parameter endpoints."""

from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class InputParameterViewSet(BaseViewSet):
    """Base viewset to read and create the input parameters.

    Attributes:
        queryset: Defined by the viewset of each parameter type.
        permission_classes: Role permissions plus the membership in the project.
        http_method_names: GET and POST only, since the parameters can't be updated
          or removed once a task is using them.
    """

    queryset = None
    permission_classes = [IsAuthenticated, RekonoModelPermission, ProjectMemberPermission]
    http_method_names = ["get", "post"]

    def get_queryset(self) -> QuerySet:
        """Get the parameters used by the tasks of the projects of the user.

        Returns:
            The parameters that the user can access, without duplicates.
        """
        return self.queryset.filter(**{f"{self.linked_model._project_field}__members": self.request.user}).distinct()

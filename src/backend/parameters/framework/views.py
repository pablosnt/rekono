from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class InputParameterViewSet(BaseViewSet):
    queryset = None
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    http_method_names = ["get", "post"]

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(**{f"{self._get_model().project_field}__members": self.request.user}).distinct()

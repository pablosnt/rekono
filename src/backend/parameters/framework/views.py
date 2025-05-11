from django.db.models import QuerySet
from framework.views import BaseViewSet
from rest_framework.permissions import IsAuthenticated
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
        model = self._get_model()
        return (
            (self.queryset if self.queryset is not None else model.objects.none())
            .filter(**{f"{model.get_project_field()}__members": self.request.user})
            .distinct()
        )

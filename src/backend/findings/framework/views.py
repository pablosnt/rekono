from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)


class FindingViewSet(BaseViewSet):
    triage_serializer_class = None
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    http_method_names = [
        "get",
        "put",
    ]

    def get_serializer_class(self) -> Serializer:
        return (
            self.triage_serializer_class
            if self.request.method == "PUT"
            else super().get_serializer_class()
        )

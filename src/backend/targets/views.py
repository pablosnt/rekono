from framework.views import BaseViewSet
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)
from targets.filters import TargetFilter
from targets.models import Target
from targets.serializers import TargetSerializer

# Create your views here.


class TargetViewSet(BaseViewSet):
    """Target ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # Fields used to search targets
    search_fields = ["target"]
    ordering_fields = ["id", "target", "type"]
    http_method_names = ["get", "post", "delete"]

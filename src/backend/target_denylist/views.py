from django.db.models import QuerySet
from framework.views import BaseViewSet
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission
from target_denylist.filters import TargetDenylistFilter
from target_denylist.models import TargetDenylist
from target_denylist.serializers import TargetDenylistSerializer

# Create your views here.


class TargetDenylistViewSet(BaseViewSet):
    queryset = TargetDenylist.objects.all()
    filterset_class = TargetDenylistFilter
    serializer_class = TargetDenylistSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["target"]
    ordering_fields = ["id", "target"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        default_queryset = super().get_queryset()
        return (
            default_queryset.filter(default=False).all()
            if self.request.method in ["PUT", "DELETE"]
            else default_queryset
        )

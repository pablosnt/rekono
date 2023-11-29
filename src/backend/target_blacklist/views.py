from django.db.models import QuerySet
from framework.views import BaseViewSet
from target_blacklist.filters import TargetBlacklistFilter
from target_blacklist.models import TargetBlacklist
from target_blacklist.serializers import TargetBlacklistSerializer

# Create your views here.


class TargetBlacklistViewSet(BaseViewSet):
    queryset = TargetBlacklist.objects.all()
    filterset_class = TargetBlacklistFilter
    serializer_class = TargetBlacklistSerializer
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

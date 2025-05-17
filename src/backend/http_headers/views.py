from django.db.models import Q, QuerySet
from framework.views import BaseViewSet
from http_headers.filters import HttpHeaderFilter
from http_headers.models import HttpHeader
from http_headers.serializers import HttpHeaderSerializer, SimpleHttpHeaderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class HttpHeaderViewSet(BaseViewSet):
    queryset = HttpHeader.objects.all()
    serializer_class = HttpHeaderSerializer
    filterset_class = HttpHeaderFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # Fields used to search input technologies
    search_fields = ["key", "value"]
    ordering_fields = ["id", "target", "user", "key"]
    http_method_names = ["get", "put", "post", "delete"]

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(Q(user=self.request.user) | Q(user__isnull=True)).filter(
            Q(target__project__members=self.request.user) | Q(target__isnull=True)
        )

    def get_serializer_class(self) -> Serializer:
        return SimpleHttpHeaderSerializer if self.request.method == "PUT" else super().get_serializer_class()

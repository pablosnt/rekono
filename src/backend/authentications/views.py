from rest_framework.permissions import IsAuthenticated

from authentications.filters import AuthenticationFilter
from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer
from framework.views import BaseViewSet
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class AuthenticationViewSet(BaseViewSet):
    """Authentication ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = Authentication.objects.all()
    serializer_class = AuthenticationSerializer
    filterset_class = AuthenticationFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "type"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

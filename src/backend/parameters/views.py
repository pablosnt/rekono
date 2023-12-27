from framework.views import BaseViewSet
from parameters.filters import InputTechnologyFilter, InputVulnerabilityFilter
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import (
    ProjectMemberPermission,
    RekonoModelPermission,
)

# Create your views here.


class InputTechnologyViewSet(BaseViewSet):
    """InputTechnology ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = InputTechnology.objects.all()
    serializer_class = InputTechnologySerializer
    filterset_class = InputTechnologyFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # Fields used to search input technologies
    search_fields = ["name", "version"]
    ordering_fields = ["id", "target", "name"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]


class InputVulnerabilityViewSet(BaseViewSet):
    """InputVulnerability ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = InputVulnerability.objects.all()
    serializer_class = InputVulnerabilitySerializer
    filterset_class = InputVulnerabilityFilter
    permission_classes = [
        IsAuthenticated,
        RekonoModelPermission,
        ProjectMemberPermission,
    ]
    # Fields used to search input vulnerabilities
    search_fields = ["cve"]
    ordering_fields = ["id", "target", "cve"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

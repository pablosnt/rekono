from drf_spectacular.utils import extend_schema
from findings.enums import OSINTDataType
from findings.filters import (
    CredentialFilter,
    ExploitFilter,
    HostFilter,
    OSINTFilter,
    PathFilter,
    PortFilter,
    TechnologyFilter,
    VulnerabilityFilter,
)
from findings.framework.views import FindingViewSet, TriageFindingViewSet
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from findings.serializers import (
    CredentialSerializer,
    ExploitSerializer,
    HostSerializer,
    OSINTSerializer,
    PathSerializer,
    PortSerializer,
    TechnologySerializer,
    VulnerabilitySerializer,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from targets.serializers import TargetSerializer

# Create your views here.


class OSINTViewSet(TriageFindingViewSet):
    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter
    search_fields = ["data"]
    ordering_fields = ["id", "data", "data_type", "source"]

    @extend_schema(request=None, responses={201: TargetSerializer})
    @action(detail=True, methods=["POST"], url_path="target", url_name="target")
    def target(self, request: Request, pk: str) -> Response:
        """Target creation from OSINT data.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        """
        osint = self.get_object()
        if osint.data_type in [
            OSINTDataType.IP,
            OSINTDataType.DOMAIN,
        ]:
            serializer = TargetSerializer(
                data={"project": osint.get_project().id, "target": osint.data}
            )
            serializer.is_valid(raise_exception=True)
            target = serializer.create(serializer.validated_data)
            return Response(
                TargetSerializer(target).data, status=status.HTTP_201_CREATED
            )
        return Response(
            {"data_type": "Target creation is not available for this OSINT data type"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class HostViewSet(FindingViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filterset_class = HostFilter
    search_fields = ["address", "os"]
    ordering_fields = ["id", "address", "os_type"]


class PortViewSet(FindingViewSet):
    queryset = Port.objects.all()
    serializer_class = PortSerializer
    filterset_class = PortFilter
    search_fields = ["port", "service"]
    ordering_fields = ["id", "host", "port", "status", "protocol", "service"]


class PathViewSet(FindingViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer
    filterset_class = PathFilter
    search_fields = ["path", "extra_info"]
    ordering_fields = ["id", "port", "port__host", "path", "status", "type"]


class TechnologyViewSet(FindingViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = ["name", "version", "description"]
    ordering_fields = ["id", "port", "name", "version"]


class CredentialViewSet(TriageFindingViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    search_fields = ["email", "username", "secret", "context"]
    ordering_fields = ["id", "email", "username", "secret"]


class VulnerabilityViewSet(TriageFindingViewSet):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    search_fields = ["name", "description", "cve", "cwe", "osvdb"]
    ordering_fields = [
        "id",
        "technology",
        "port",
        "name",
        "severity",
        "cve",
        "cwe",
        "osvdb",
    ]


class ExploitViewSet(TriageFindingViewSet):
    queryset = Exploit.objects.all()
    serializer_class = ExploitSerializer
    filterset_class = ExploitFilter
    search_fields = ["title", "edb_id", "reference"]
    ordering_fields = [
        "id",
        "vulnerability",
        "technology",
        "title",
        "edb_id",
        "reference",
    ]

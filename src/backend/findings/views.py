"""Django REST framework views for findings API.

This module provides ViewSet classes for all finding types, offering
CRUD operations and additional custom actions through the REST API.
Each ViewSet extends the base finding ViewSets to provide standardized
functionality while allowing for custom behavior specific to each
finding type.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

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
from targets.serializers import TargetSerializer


class OSINTViewSet(TriageFindingViewSet):
    """ViewSet for OSINT findings.

    Provides operations for Open Source Intelligence findings
    and includes a custom action to create targets from OSINT data.
    """

    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter
    search_fields = ["data"]
    ordering_fields = ["id", "data", "data_type", "source"]

    @extend_schema(request=None, responses={201: TargetSerializer})
    @action(detail=True, methods=["POST"])
    def target(self, request: Request, pk: str) -> Response:
        """Create a target from OSINT data.

        Converts OSINT findings (IP addresses or domains) into target
        objects for further security assessment.

        Args:
            request: The HTTP request object.
            pk: Primary key of the OSINT finding.

        Returns:
            Response with the created target data or error message.
        """
        osint = self.get_object_or_404()
        if osint.data_type in [
            OSINTDataType.IP,
            OSINTDataType.DOMAIN,
        ]:
            serializer = TargetSerializer(
                data={"project": osint.parent_project.id, "target": osint.data}, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            target = serializer.create(serializer.validated_data)
            return Response(
                TargetSerializer(instance=target, context={"request": request}).data, status=status.HTTP_201_CREATED
            )
        return Response(
            {"data_type": "Target creation is not available for this OSINT data type"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class HostViewSet(FindingViewSet):
    """ViewSet for host findings.

    Provides operations for discovered network hosts,
    including search and filtering capabilities.
    """

    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filterset_class = HostFilter
    search_fields = ["ip", "domain", "os", "country", "city"]
    ordering_fields = ["id", "ip", "domain", "os_type", "country", "city"]


class PortViewSet(FindingViewSet):
    """ViewSet for port findings.

    Provides operations for discovered network ports,
    including search and filtering capabilities.
    """

    queryset = Port.objects.all()
    serializer_class = PortSerializer
    filterset_class = PortFilter
    search_fields = ["port", "service"]
    ordering_fields = ["id", "host", "port", "status", "protocol", "service"]


class PathViewSet(FindingViewSet):
    """ViewSet for path findings.

    Provides operations for discovered web paths and endpoints,
    including search and filtering capabilities.
    """

    queryset = Path.objects.all()
    serializer_class = PathSerializer
    filterset_class = PathFilter
    search_fields = ["path", "extra_info"]
    ordering_fields = ["id", "port", "port__host", "port__port", "path", "status", "type"]


class TechnologyViewSet(FindingViewSet):
    """ViewSet for technology findings.

    Provides operations for discovered technologies and services,
    including search and filtering capabilities.
    """

    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = ["name", "version", "description"]
    ordering_fields = ["id", "port", "port__host", "port__port", "name", "version"]


class CredentialViewSet(TriageFindingViewSet):
    """ViewSet for credential findings.

    Provides operations for discovered credentials,
    including search and filtering capabilities.
    """

    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    search_fields = ["email", "username", "secret", "context"]
    ordering_fields = ["id", "technology", "email", "username", "secret"]


class VulnerabilityViewSet(TriageFindingViewSet):
    """ViewSet for vulnerability findings.

    Provides operations for discovered vulnerabilities,
    including search and filtering capabilities.
    """

    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    search_fields = ["name", "description", "cve", "cwe"]
    ordering_fields = ["id", "technology", "port", "name", "severity", "cve", "cwe"]


class ExploitViewSet(TriageFindingViewSet):
    """ViewSet for exploit findings.

    Provides operations for discovered exploits,
    including search and filtering capabilities.
    """

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

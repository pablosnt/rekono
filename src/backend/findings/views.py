"""ViewSets for findings REST API endpoints.

Provides ViewSet classes for all finding types with CRUD operations,
filtering, search capabilities, and custom actions for security findings
management through the REST API.
"""

from django.shortcuts import get_object_or_404
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
    """ViewSet for Open Source Intelligence findings management.

    Provides CRUD operations for OSINT findings with triage capabilities
    and target creation functionality for IP and domain data types.

    Custom Actions:
        target: Create a target from OSINT data for IP/Domain types

    Attributes:
        queryset (QuerySet): All OSINT objects
        serializer_class (Serializer): OSINTSerializer for OSINT operations
        filterset_class (FilterSet): OSINTFilter for querying OSINT findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
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

        Converts OSINT findings with IP or Domain data types into target
        objects for further security assessment.

        Args:
            request (Request): HTTP request object.
            pk (str): Primary key of the OSINT finding.

        Returns:
            Response: Created target data (201) or error message (400).
        """
        osint = get_object_or_404(self.get_queryset(), pk=pk)
        if osint.data_type in [OSINTDataType.IP, OSINTDataType.DOMAIN]:
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
    """ViewSet for network host findings management.

    Provides CRUD operations for discovered network hosts with
    search and filtering capabilities for asset inventory.

    Attributes:
        queryset (QuerySet): All Host objects
        serializer_class (Serializer): HostSerializer for host operations
        filterset_class (FilterSet): HostFilter for querying host findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filterset_class = HostFilter
    search_fields = ["ip", "domain", "os", "country", "city"]
    ordering_fields = ["id", "ip", "domain", "os_type", "country", "city"]


class PortViewSet(FindingViewSet):
    """ViewSet for network port findings management.

    Provides CRUD operations for discovered network ports and services
    with search and filtering capabilities for attack surface enumeration.

    Attributes:
        queryset (QuerySet): All Port objects
        serializer_class (Serializer): PortSerializer for port operations
        filterset_class (FilterSet): PortFilter for querying port findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Port.objects.all()
    serializer_class = PortSerializer
    filterset_class = PortFilter
    search_fields = ["port", "service"]
    ordering_fields = ["id", "host", "port", "status", "protocol", "service"]


class PathViewSet(FindingViewSet):
    """ViewSet for web path findings management.

    Provides CRUD operations for discovered web paths and endpoints
    with search and filtering capabilities for web application analysis.

    Attributes:
        queryset (QuerySet): All Path objects
        serializer_class (Serializer): PathSerializer for path operations
        filterset_class (FilterSet): PathFilter for querying path findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Path.objects.all()
    serializer_class = PathSerializer
    filterset_class = PathFilter
    search_fields = ["path", "extra_info"]
    ordering_fields = ["id", "port", "port__host", "port__port", "path", "status", "type"]


class TechnologyViewSet(FindingViewSet):
    """ViewSet for technology findings management.

    Provides CRUD operations for discovered software technologies
    with search and filtering capabilities for technology stack analysis.

    Attributes:
        queryset (QuerySet): All Technology objects
        serializer_class (Serializer): TechnologySerializer for technology operations
        filterset_class (FilterSet): TechnologyFilter for querying technology findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = ["name", "version", "description"]
    ordering_fields = ["id", "port", "port__host", "port__port", "name", "version"]


class CredentialViewSet(TriageFindingViewSet):
    """ViewSet for credential findings management.

    Provides CRUD operations for discovered credentials with triage
    capabilities and search/filtering for credential exposure analysis.

    Attributes:
        queryset (QuerySet): All Credential objects
        serializer_class (Serializer): CredentialSerializer for credential operations
        filterset_class (FilterSet): CredentialFilter for querying credential findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    search_fields = ["email", "username", "secret", "context"]
    ordering_fields = ["id", "technology", "email", "username", "secret"]


class VulnerabilityViewSet(TriageFindingViewSet):
    """ViewSet for vulnerability findings management.

    Provides CRUD operations for discovered vulnerabilities with triage
    capabilities and search/filtering for vulnerability assessment.

    Attributes:
        queryset (QuerySet): All Vulnerability objects
        serializer_class (Serializer): VulnerabilitySerializer for vulnerability operations
        filterset_class (FilterSet): VulnerabilityFilter for querying vulnerability findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    search_fields = ["name", "description", "cve", "cwe"]
    ordering_fields = ["id", "technology", "port", "name", "severity", "cve", "cwe"]


class ExploitViewSet(TriageFindingViewSet):
    """ViewSet for exploit findings management.

    Provides CRUD operations for discovered exploits with triage
    capabilities and search/filtering for exploit availability analysis.

    Attributes:
        queryset (QuerySet): All Exploit objects
        serializer_class (Serializer): ExploitSerializer for exploit operations
        filterset_class (FilterSet): ExploitFilter for querying exploit findings
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
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

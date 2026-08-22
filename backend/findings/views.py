"""Viewsets of the finding endpoints.

The findings can only be read, fixed, and triaged, since they are created by the
tools instead of by the users. The only exception is the target creation from an
OSINT finding, which turns a discovered domain or IP address into a new target.
"""

from django.db.models import Max
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from findings.enums import OSINTDataType, TriageStatus
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
from framework.views import LatestViewSet
from targets.serializers import TargetSerializer


class OSINTViewSet(TriageFindingViewSet):
    """Read and triage the data found on public sources.

    Attributes:
        queryset: All the OSINT findings, filtered later by project membership.
        serializer_class: Serializer of the OSINT findings.
        filterset_class: Filters of the OSINT findings.
        search_fields: Free text search over the discovered data.
        ordering_fields: Fields that the OSINT findings can be sorted by.
    """

    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter
    search_fields = ["data"]
    ordering_fields = ["id", "data", "data_type", "source"]

    @extend_schema(request=None, responses={201: TargetSerializer})
    @action(detail=True, methods=["POST"])
    def target(self, request: Request, pk: str) -> Response:
        """Create a new target in the project from the discovered data.

        Args:
            request: Request that asks for the target to be created.
            pk: Identifier of the OSINT finding, taken from the URL.

        Returns:
            The created target, or a validation error if the data can't be
            scanned, since only the IP addresses and the domains can be targets.
        """
        osint = self.get_object()
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
    """Read and fix the hosts found in the network.

    Attributes:
        queryset: All the hosts, filtered later by project membership.
        serializer_class: Serializer of the hosts.
        filterset_class: Filters of the hosts.
        search_fields: Free text search over the host identity and its location.
        ordering_fields: Fields that the hosts can be sorted by.
    """

    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filterset_class = HostFilter
    search_fields = ["ip", "domain", "os", "country", "city"]
    ordering_fields = ["id", "ip", "domain", "os_type", "country", "city"]


class PortViewSet(FindingViewSet):
    """Read and fix the ports found in the hosts.

    Attributes:
        queryset: All the ports, filtered later by project membership.
        serializer_class: Serializer of the ports.
        filterset_class: Filters of the ports.
        search_fields: Free text search over the port number and its service.
        ordering_fields: Fields that the ports can be sorted by.
    """

    queryset = Port.objects.all()
    serializer_class = PortSerializer
    filterset_class = PortFilter
    search_fields = ["port", "service"]
    ordering_fields = ["id", "host", "port", "status", "protocol", "service"]


class PathViewSet(FindingViewSet):
    """Read and fix the paths found in the ports.

    Attributes:
        queryset: All the paths, filtered later by project membership.
        serializer_class: Serializer of the paths.
        filterset_class: Filters of the paths.
        search_fields: Free text search over the path and its extra data.
        ordering_fields: Fields that the paths can be sorted by.
    """

    queryset = Path.objects.all()
    serializer_class = PathSerializer
    filterset_class = PathFilter
    search_fields = ["path", "extra_info"]
    ordering_fields = ["id", "port", "port__host", "port__port", "path", "status", "type"]


class TechnologyViewSet(FindingViewSet):
    """Read and fix the technologies found in the ports.

    Attributes:
        queryset: All the technologies, filtered later by project membership.
        serializer_class: Serializer of the technologies.
        filterset_class: Filters of the technologies.
        search_fields: Free text search over the technology and its description.
        ordering_fields: Fields that the technologies can be sorted by.
    """

    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = ["name", "version", "description"]
    ordering_fields = ["id", "port", "port__host", "port__port", "name", "version"]


class CredentialViewSet(TriageFindingViewSet):
    """Read, triage, and fix the credentials exposed in the technologies.

    Attributes:
        queryset: All the credentials, filtered later by project membership.
        serializer_class: Serializer of the credentials.
        filterset_class: Filters of the credentials.
        search_fields: Free text search over the credential data and its context.
        ordering_fields: Fields that the credentials can be sorted by.
    """

    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    search_fields = ["email", "username", "secret", "context"]
    ordering_fields = ["id", "technology", "email", "username", "secret"]


class VulnerabilityViewSet(TriageFindingViewSet):
    """Read, triage, and fix the vulnerabilities found in the technologies and ports.

    Attributes:
        queryset: All the vulnerabilities, filtered later by project membership.
        serializer_class: Serializer of the vulnerabilities.
        filterset_class: Filters of the vulnerabilities.
        search_fields: Free text search over the vulnerability identity and its
          identifiers in the vulnerability databases.
        ordering_fields: Fields that the vulnerabilities can be sorted by.
    """

    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    search_fields = ["name", "description", "cve", "euvd_id", "ghsa_id", "osv_generic_id", "cwes"]
    ordering_fields = [
        "id",
        "technology",
        "port",
        "name",
        "severity",
        "cvss_base_score",
        "cve",
        "euvd_id",
        "ghsa_id",
        "osv_generic_id",
        "cwes",
        "epss_score",
        "epss_percentile",
    ]


class ExploitViewSet(TriageFindingViewSet):
    """Read, triage, and fix the exploits found for the vulnerabilities.

    Attributes:
        queryset: All the exploits, filtered later by project membership.
        serializer_class: Serializer of the exploits.
        filterset_class: Filters of the exploits.
        search_fields: Free text search over the exploit identity and its source.
        ordering_fields: Fields that the exploits can be sorted by.
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


class LatestHostsViewSet(LatestViewSet):
    """Read the hosts that have been discovered most recently.

    Attributes:
        queryset: Hosts that are still not fixed, annotated with the start date of
          the last execution that found them.
        ordering: The most recently discovered hosts first.
        serializer_class: Serializer of the hosts.
        filterset_class: Filters of the hosts.
    """

    queryset = Host.objects.filter(is_fixed=False).annotate(latest=Max("executions__start"))
    ordering = ["-latest"]
    serializer_class = HostSerializer
    filterset_class = HostFilter


class LatestVulnerabilitiesViewSet(LatestViewSet):
    """Read the vulnerabilities that have been discovered most recently.

    Attributes:
        queryset: Vulnerabilities that are still not fixed and that the auditors
          haven't discarded, annotated with the start date of the last execution
          that found them. The ones created by the users are excluded, since they
          weren't discovered by any execution.
        ordering: The most recently discovered vulnerabilities first.
        serializer_class: Serializer of the vulnerabilities.
        filterset_class: Filters of the vulnerabilities.
    """

    queryset = (
        Vulnerability.objects.filter(is_fixed=False, created_from_user_input=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .annotate(latest=Max("executions__start"))
    )
    ordering = ["-latest"]
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter

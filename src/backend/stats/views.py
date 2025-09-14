"""Django REST framework views for statistics and analytics endpoints.

Provides API views for retrieving various security statistics including vulnerability
analytics, host metrics, queue monitoring, trending data, and evolution analysis.
Supports filtering, pagination, and aggregation for comprehensive security reporting.
"""

from django.db.models import Count, F, Func, Max, OuterRef, Q, Subquery
from django.db.models.functions import TruncDate
from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from findings.enums import Severity, TriageStatus
from findings.filters import (
    CredentialFilter,
    ExploitFilter,
    HostFilter,
    OSINTFilter,
    PortFilter,
    TechnologyFilter,
    VulnerabilityFilter,
)
from findings.models import OSINT, Credential, Exploit, Host, Port, Technology, Vulnerability
from findings.serializers import HostSerializer, VulnerabilitySerializer
from framework.views import BaseViewSet
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectSerializer
from security.authorization.permissions import IsAdmin
from stats.serializers import (
    EvolutionPerSeverityStatsSerializer,
    EvolutionStatsSerializer,
    HostStatsSerializer,
    HostVulnerabilitiesStatsSerializer,
    PortStatsSerializer,
    RQStatsSerializer,
    TechnologyStatsSerializer,
    TriagingStatsSerializer,
    VulnerabilityCountPerIsFixedSerializer,
    VulnerabilityCVEStatsSerializer,
    VulnerabilityCWEStatsSerializer,
    VulnerabilitySeverityStatsSerializer,
)
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.serializers import TaskSerializer


class RQStatsView(APIView):
    """API view for Redis Queue (RQ) statistics monitoring.

    Provides real-time statistics about background job queues including
    job counts, worker status, and queue health for system monitoring.
    Requires admin permissions for access.

    Attributes:
        permission_classes: Restricts access to admin users only
    """

    permission_classes = [IsAdmin]

    @extend_schema(request=None, responses=RQStatsSerializer)
    def get(self, request: Request) -> Response:
        """Retrieve current Redis Queue statistics.

        Returns comprehensive queue statistics including job counts,
        worker information, and queue status across all queue types.

        Args:
            request: HTTP request object

        Returns:
            Response containing queue statistics data
        """
        return Response(
            RQStatsSerializer(
                {
                    queue["name"]: {
                        k: v
                        for k, v in queue.items()
                        if k
                        in [
                            "jobs",
                            "workers",
                            "finished_jobs",
                            "started_jobs",
                            "deferred_jobs",
                            "failed_jobs",
                            "scheduled_jobs",
                        ]
                    }
                    for queue in get_statistics().get("queues", [])
                },
                context={"request": request},
            ).data,
            status=HTTP_200_OK,
        )


class StatsViewSet(BaseViewSet):
    """Base viewset for statistics endpoints.

    Provides common configuration for all statistics views including
    authentication requirements and HTTP method restrictions.

    Attributes:
        ordering_fields: No custom ordering fields defined
        http_method_names: Restricted to GET requests only
        permission_classes: Requires authenticated users
    """

    ordering = []
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]


class LatestViewSet(StatsViewSet):
    """Base viewset for retrieving latest items statistics.

    Extends StatsViewSet to provide functionality for fetching the most
    recent items with a configurable limit and no pagination.

    Attributes:
        top_items: Maximum number of items to return (default: 5)
        pagination_class: Pagination disabled for latest views
    """

    top_items = 5
    pagination_class = None

    def filter_queryset(self, queryset):
        """Apply filtering and limit results to top items.

        Args:
            queryset: Base queryset to filter

        Returns:
            Filtered queryset limited to top_items count
        """
        queryset = super().filter_queryset(queryset)
        return queryset[: self.top_items]


class LatestTasksViewSet(LatestViewSet):
    """ViewSet for retrieving latest task execution statistics.

    Provides the most recently started tasks, excluding those without
    a start time. Ordered by start time in descending order.

    Attributes:
        queryset: Tasks with non-null start times
        ordering: Most recent tasks first
        serializer_class: Task serialization
        filterset_class: Task filtering capabilities
    """

    queryset = Task.objects.exclude(start=None)
    ordering = ["-start"]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter


class LatestHostsViewSet(LatestViewSet):
    """ViewSet for retrieving latest discovered host statistics.

    Provides the most recently discovered hosts that are not fixed,
    annotated with their latest execution timestamp.

    Attributes:
        queryset: Unfixed hosts with latest execution annotations
        ordering: Most recently discovered hosts first
        serializer_class: Host serialization
        filterset_class: Host filtering capabilities
    """

    queryset = Host.objects.filter(is_fixed=False).annotate(latest=Max("executions__start"))
    ordering = ["-latest"]
    serializer_class = HostSerializer
    filterset_class = HostFilter


class LatestVulnerabilitiesViewSet(LatestViewSet):
    """ViewSet for retrieving latest vulnerability statistics.

    Provides the most recently discovered vulnerabilities that are unfixed
    and not marked as false positives, with latest execution timestamps.

    Attributes:
        queryset: Active vulnerabilities with latest execution annotations
        ordering: Most recently discovered vulnerabilities first
        serializer_class: Vulnerability serialization
        filterset_class: Vulnerability filtering capabilities
    """

    queryset = (
        Vulnerability.objects.filter(is_fixed=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .annotate(latest=Max("executions__start"))
    )
    ordering = ["-latest"]
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter


class TopProjectsViewSet(LatestViewSet):
    """ViewSet for retrieving top project statistics by activity.

    Provides projects ranked by security findings and activity metrics,
    annotated with counts of targets, tasks, hosts, and vulnerabilities.

    Attributes:
        queryset: Projects with comprehensive activity annotations
        ordering: Prioritizes projects with most vulnerabilities and activity
        serializer_class: Project serialization
        filterset_class: Project filtering capabilities
    """

    queryset = (
        Project.objects.annotate(targets_count=Count("targets", distinct=True))
        .annotate(tasks_count=Count("targets__tasks", distinct=True))
        .annotate(
            hosts_count=Count(
                "targets__tasks__executions__host",
                distinct=True,
                filter=Q(targets__tasks__executions__host__is_fixed=False),
            )
        )
        .annotate(
            vulnerabilities_count=Count(
                "targets__tasks__executions__vulnerability",
                distinct=True,
                filter=~Q(targets__tasks__executions__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE)
                & Q(targets__tasks__executions__vulnerability__is_fixed=False),
            )
        )
    )
    ordering = ["-vulnerabilities_count", "-hosts_count", "-tasks_count", "-targets_count"]
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter


class HostStatsViewSet(StatsViewSet):
    """ViewSet for host statistics grouped by operating system type.

    Provides aggregated counts of discovered hosts categorized by their
    operating system family for infrastructure analysis.

    Attributes:
        queryset: Unfixed hosts grouped by OS type with counts
        ordering: Most common OS types first, then alphabetical
        serializer_class: Host statistics serialization
        filterset_class: Host filtering capabilities
        pagination_class: Pagination disabled for complete statistics
    """

    queryset = Host.objects.filter(is_fixed=False).values("os_type").annotate(count=Count("os_type"))
    ordering = ["-count", "os_type"]
    serializer_class = HostStatsSerializer
    filterset_class = HostFilter
    pagination_class = None


class HostVulnerabilitiesStatsViewSet(StatsViewSet):
    """ViewSet for detailed host vulnerability statistics.

    Provides comprehensive vulnerability counts per host including total
    counts by fix status and breakdown by severity levels for targeted
    remediation efforts.

    Attributes:
        queryset: Hosts with detailed vulnerability count annotations
        ordering: Prioritizes hosts with most open vulnerabilities
        serializer_class: Host vulnerability statistics serialization
        filterset_class: Host filtering capabilities
    """

    queryset = (
        Host.objects.filter(is_fixed=False)
        .values("id", "ip", "domain")
        .annotate(
            open=Subquery(
                Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .filter(Q(port__host__pk=OuterRef("pk")) | Q(technology__port__host__pk=OuterRef("pk")))
                .filter(is_fixed=False)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
        )
        .annotate(
            fixed=Subquery(
                Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .filter(Q(port__host=OuterRef("pk")) | Q(technology__port__host=OuterRef("pk")))
                .filter(is_fixed=True)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
        )
        .annotate(
            **{
                severity.name.lower(): Subquery(
                    Vulnerability.objects.exclude(is_fixed=True)
                    .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                    .filter(Q(port__host=OuterRef("pk")) | Q(technology__port__host=OuterRef("pk")))
                    .filter(severity=severity)
                    .annotate(count=Func(F("id"), function="Count"))
                    .values("count")
                )
                for severity in Severity
            },
        )
    )
    ordering = ["-open", "-fixed", "-critical", "-high", "-medium", "-low", "-info", "-id"]
    serializer_class = HostVulnerabilitiesStatsSerializer
    filterset_class = HostFilter


# TODO: In addition to hosts/detection-date, create stats for getting hosts exposure evolution (first detection to mitigation date/today)
class HostEvolutionStatsViewSet(StatsViewSet):
    """ViewSet for host discovery evolution statistics over time.

    Provides time-series data showing host discovery trends by date
    for tracking reconnaissance and asset discovery progress.

    Attributes:
        queryset: Hosts grouped by discovery date with counts
        ordering: Most recent discoveries first
        serializer_class: Evolution statistics serialization
        filterset_class: Host filtering capabilities
    """

    queryset = (
        Host.objects.prefetch_related("executions")
        .annotate(date=TruncDate("executions__start"))
        .values("date")
        .annotate(count=Count("date"))
    )
    ordering = ["-date"]
    serializer_class = EvolutionStatsSerializer
    filterset_class = HostFilter


class PortStatsViewSet(StatsViewSet):
    """ViewSet for network port and service statistics.

    Provides aggregated statistics for discovered network services including
    port numbers, protocols, and service identification for attack surface analysis.

    Attributes:
        queryset: Unfixed ports grouped by service details with counts
        ordering: Most common services first, then by service/port/protocol
        serializer_class: Port statistics serialization
        filterset_class: Port filtering capabilities
    """

    queryset = (
        Port.objects.filter(is_fixed=False).values("service", "protocol", "port").annotate(count=Count("service"))
    )
    ordering = ["-count", "service", "port", "protocol"]
    serializer_class = PortStatsSerializer
    filterset_class = PortFilter


class TechnologyStatsViewSet(StatsViewSet):
    """ViewSet for technology fingerprinting statistics.

    Provides counts of identified technologies and software components
    across discovered assets for technology stack analysis.

    Attributes:
        queryset: Unfixed technologies grouped by name with counts
        ordering: Most common technologies first, then alphabetical
        serializer_class: Technology statistics serialization
        filterset_class: Technology filtering capabilities
    """

    queryset = Technology.objects.filter(is_fixed=False).values("name").annotate(count=Count("name"))
    ordering = ["-count", "name"]
    serializer_class = TechnologyStatsSerializer
    filterset_class = TechnologyFilter


class VulnerabilityTrendingStatsViewSet(StatsViewSet):
    """ViewSet for trending vulnerability statistics by CVE.

    Provides statistics for vulnerabilities marked as trending, grouped by
    CVE identifier with severity information and reference links.

    Attributes:
        queryset: Active trending vulnerabilities with CVE annotations
        ordering: Most critical open vulnerabilities first
        serializer_class: CVE vulnerability statistics serialization
        filterset_class: Vulnerability filtering capabilities
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .filter(trending=True)
        .exclude(cve=None)
        .annotate(link=Max("reference"))
        .annotate(severity_value=Max("severity"))
        .values("cve", "severity_value", "link")
        .annotate(open=Count("cve", filter=Q(is_fixed=False)))
        .annotate(fixed=Count("cve", filter=Q(is_fixed=True)))
    )
    ordering = ["-open", "-severity_value", "cve"]
    serializer_class = VulnerabilityCVEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityCVEStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability statistics grouped by CVE identifier.

    Provides comprehensive vulnerability counts by CVE with severity levels
    and reference links for vulnerability management and tracking.

    Attributes:
        queryset: Active vulnerabilities with CVE data and annotations
        ordering: Most critical open vulnerabilities first
        serializer_class: CVE vulnerability statistics serialization
        filterset_class: Vulnerability filtering capabilities
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .exclude(cve=None)
        .annotate(link=Max("reference"))
        .annotate(severity_value=Max("severity"))
        .values("cve", "severity_value", "link")
        .annotate(open=Count("cve", filter=Q(is_fixed=False)))
        .annotate(fixed=Count("cve", filter=Q(is_fixed=True)))
    )
    ordering = ["-open", "-severity_value", "cve"]
    serializer_class = VulnerabilityCVEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityCWEStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability statistics grouped by CWE identifier.

    Provides vulnerability counts categorized by Common Weakness Enumeration
    identifiers for vulnerability pattern analysis and remediation planning.

    Attributes:
        queryset: Active vulnerabilities grouped by CWE with counts
        ordering: Most prevalent open vulnerabilities first
        serializer_class: CWE vulnerability statistics serialization
        filterset_class: Vulnerability filtering capabilities
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .exclude(cwe=None)
        .values("cwe")
        .annotate(open=Count("cwe", filter=Q(is_fixed=False)))
        .annotate(fixed=Count("cwe", filter=Q(is_fixed=True)))
    )
    ordering = ["-open", "cwe"]
    serializer_class = VulnerabilityCWEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilitySeverityStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability statistics grouped by severity level.

    Provides vulnerability counts categorized by severity rating for
    security prioritization and risk assessment analysis.

    Attributes:
        queryset: Active vulnerabilities grouped by severity with counts
        ordering: Most severe vulnerabilities first
        serializer_class: Severity vulnerability statistics serialization
        filterset_class: Vulnerability filtering capabilities
        pagination_class: Pagination disabled for complete severity breakdown
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .values("severity")
        .annotate(open=Count("severity", filter=Q(is_fixed=False)))
        .annotate(fixed=Count("severity", filter=Q(is_fixed=True)))
    )
    ordering = ["-severity"]
    serializer_class = VulnerabilitySeverityStatsSerializer
    filterset_class = VulnerabilityFilter
    pagination_class = None


# TODO: In addition to vulns/detection-date, create stats for getting vulns exposure window (first detection to mitigation date/today)
class VulnerabilityEvolutionStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability discovery evolution statistics over time.

    Provides time-series data showing vulnerability discovery trends by date
    and severity level for tracking security posture changes over time.

    Attributes:
        queryset: Vulnerabilities grouped by discovery date and severity with counts
        ordering: Most recent and severe vulnerabilities first
        serializer_class: Evolution per severity statistics serialization
        filterset_class: Vulnerability filtering capabilities
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .prefetch_related("executions")
        .annotate(date=TruncDate("executions__start"))
        .values("date", "severity")
        .annotate(count=Count("date"))
    )
    ordering = ["-date", "-severity"]
    serializer_class = EvolutionPerSeverityStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityStatusStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability statistics grouped by fix status.

    Provides high-level counts of vulnerabilities categorized by their
    remediation status for overall security posture assessment.

    Attributes:
        queryset: Active vulnerabilities grouped by fix status with counts
        ordering: Fixed status ordering (false first, then true)
        serializer_class: Fix status statistics serialization
        filterset_class: Vulnerability filtering capabilities
        pagination_class: Pagination disabled for complete status overview
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .values("is_fixed")
        .annotate(count=Count("id", distinct=True))
    )
    ordering = ["is_fixed"]
    serializer_class = VulnerabilityCountPerIsFixedSerializer
    filterset_class = VulnerabilityFilter
    pagination_class = None


class VulnerabilityStatusPerServerityStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability fix status statistics grouped by severity.

    Provides detailed breakdown of vulnerability remediation progress
    categorized by severity level for targeted security improvements.

    Attributes:
        queryset: Active vulnerabilities with fix counts by severity
        ordering: Most severe vulnerabilities first
        serializer_class: Severity vulnerability statistics serialization
        filterset_class: Vulnerability filtering capabilities
        pagination_class: Pagination disabled for complete severity breakdown
    """

    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .values("severity")
        .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
        .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
    )
    ordering = ["-severity"]
    serializer_class = VulnerabilitySeverityStatsSerializer
    filterset_class = VulnerabilityFilter
    pagination_class = None


class TriagingStatsViewSet(StatsViewSet):
    """ViewSet for security finding triage statistics across all finding types.

    Provides comprehensive triage status statistics by aggregating counts
    across OSINT, credentials, vulnerabilities, and exploits findings.

    Attributes:
        queryset: Base OSINT findings grouped by triage status
        ordering: No specific ordering applied
        serializer_class: Triaging statistics serialization
        filterset_class: OSINT filtering capabilities (base filter)
        pagination_class: Pagination disabled for complete triage overview
    """

    queryset = (
        OSINT.objects.values("triage_status")
        .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
        .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
    )
    serializer_class = TriagingStatsSerializer
    filterset_class = OSINTFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        """Apply filtering and aggregate triage statistics across all finding types.

        Combines triage status counts from OSINT, Credential, Vulnerability,
        and Exploit models to provide comprehensive triage statistics.

        Args:
            queryset: Base OSINT queryset to filter

        Returns:
            List of aggregated triage status statistics across all finding types
        """
        queryset = super().filter_queryset(queryset)
        # This is needed because it's not possible to union multiple querysets
        # and then get counts grouped by triage_status
        count_per_status = {item["triage_status"]: item for item in queryset}
        for filterset_class, model in [
            (CredentialFilter, Credential),
            (VulnerabilityFilter, Vulnerability),
            (ExploitFilter, Exploit),
        ]:
            self.filterset_class = filterset_class
            new_queryset = super().filter_queryset(
                model.objects.values("triage_status")
                .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
                .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
            )
            for item in new_queryset:
                if item["triage_status"] in count_per_status:
                    for field in ["open", "fixed"]:
                        count_per_status[item["triage_status"]][field] += item[field]
                else:
                    count_per_status[item["triage_status"]] = item
        self.filterset_class = OSINTFilter
        return list(dict(sorted(count_per_status.items())).values())

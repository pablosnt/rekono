"""Django REST framework views for statistics and analytics endpoints.

Provides API views for retrieving various security statistics including vulnerability
analytics, host metrics, queue monitoring, trending data, and evolution analysis.
Supports filtering, pagination, and aggregation for comprehensive security reporting.
"""

import datetime

from django.db.models import Count, Exists, F, Func, Max, Min, OuterRef, Q, Subquery
from django.db.models.functions import TruncMonth
from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema
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
    PathFilter,
    PortFilter,
    TechnologyFilter,
    VulnerabilityFilter,
)
from findings.framework.models import TriageFinding
from findings.models import OSINT, Credential, Exploit, Host, Port, Technology, Vulnerability
from framework.views import StatsViewSet
from security.authorization.permissions import IsAdmin
from stats.serializers import (
    ExploitCoverageStatsSerializer,
    FindingsEvolutionStatsSerializer,
    HostStatsSerializer,
    HostVulnerabilitiesStatsSerializer,
    PortStatsSerializer,
    RQStatsSerializer,
    TechnologyStatsSerializer,
    TriagingStatsSerializer,
    VulnerabilityCVEStatsSerializer,
    VulnerabilityCWEStatsSerializer,
    VulnerabilitySeverityStatsSerializer,
)


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

    queryset = Host.objects.filter(is_fixed=False).values("os_type").annotate(count=Count("id", distinct=True))
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
                .filter(is_fixed=False, created_from_user_input=False)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
        )
        .annotate(
            fixed=Subquery(
                Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .filter(Q(port__host=OuterRef("pk")) | Q(technology__port__host=OuterRef("pk")))
                .filter(is_fixed=True, created_from_user_input=False)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
        )
        .annotate(
            **{
                severity.name.lower(): Subquery(
                    Vulnerability.objects.filter(is_fixed=False, created_from_user_input=False)
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
        Port.objects.filter(is_fixed=False, service__isnull=False, protocol__isnull=False, port__isnull=False)
        .exclude(service="")
        .exclude(protocol="")
        .values("service", "protocol", "port")
        .annotate(count=Count("id", distinct=True))
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

    queryset = (
        Technology.objects.filter(is_fixed=False, created_from_user_input=False)
        .values("name")
        .annotate(count=Count("id", distinct=True))
    )
    ordering = ["-count", "name"]
    serializer_class = TechnologyStatsSerializer
    filterset_class = TechnologyFilter


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
        Vulnerability.objects.filter(created_from_user_input=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(cve=None)
        .annotate(link=Max("reference"))
        .annotate(severity_value=Max("severity"))
        .values("cve", "severity_value", "link")
        .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
        .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
    )
    ordering = ["-open", "-severity_value", "cve"]
    serializer_class = VulnerabilityCVEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityCWEStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability statistics grouped by CWE identifier.

    Provides vulnerability counts categorized by Common Weakness Enumeration
    identifiers for vulnerability pattern analysis and remediation planning.
    Uses Python-side aggregation because cwes is a JSONField; the primary CWE
    for grouping is cwes[-1] (the highest-numbered entry, kept sorted on save).

    Attributes:
        queryset: Base filtered vulnerabilities (aggregation done in filter_queryset)
        serializer_class: CWE vulnerability statistics serialization
        filterset_class: Vulnerability filtering capabilities
        pagination_class: Standard pagination for results
    """

    queryset = (
        Vulnerability.objects.filter(created_from_user_input=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(cwes=None)
        .exclude(cwes=[])
        .annotate(cwe=F("cwes__-1"))
        .values("cwe")
        .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
        .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
    )

    ordering = ["-open", "cwe"]
    serializer_class = VulnerabilityCWEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityStatusStatsViewSet(StatsViewSet):
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
        Vulnerability.objects.filter(created_from_user_input=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .values("severity")
        .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
        .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
    )
    ordering = ["-severity"]
    serializer_class = VulnerabilitySeverityStatsSerializer
    filterset_class = VulnerabilityFilter
    pagination_class = None


class VulnerabilityExploitCoverageStatsViewSet(StatsViewSet):
    """ViewSet for vulnerability exploit coverage statistics.

    Provides counts of open vulnerabilities grouped by whether public exploit
    code is available, enabling prioritization of exploitable vulnerabilities.

    Attributes:
        queryset: Open vulnerabilities annotated with exploit availability
        serializer_class: Exploit coverage statistics serialization
        filterset_class: Vulnerability filtering capabilities
        pagination_class: Pagination disabled for complete coverage overview
        ordering: False (no exploits) first, then True (has exploits)
    """

    queryset = (
        Vulnerability.objects.filter(is_fixed=False, created_from_user_input=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .annotate(has_exploits=Exists(Exploit.objects.filter(vulnerability=OuterRef("pk"))))
        .values("has_exploits")
        .annotate(count=Count("id", distinct=True))
    )
    serializer_class = ExploitCoverageStatsSerializer
    filterset_class = VulnerabilityFilter
    pagination_class = None
    ordering = ["has_exploits"]


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

    queryset = OSINT.objects.all()
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
        # This is needed because it's not possible to union multiple querysets
        # and then get counts grouped by triage_status
        count_per_status = {}
        for filterset_class, model in [
            (OSINTFilter, OSINT),
            (CredentialFilter, Credential),
            (VulnerabilityFilter, Vulnerability),
            (ExploitFilter, Exploit),
        ]:
            self.filterset_class = filterset_class
            new_queryset = super().filter_queryset(
                model.objects.filter(created_from_user_input=False)
                .values("triage_status")
                .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
                .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
            )
            for item in new_queryset:
                if item["triage_status"] in count_per_status:
                    for field in ["open", "fixed"]:
                        count_per_status[item["triage_status"]][field] += item[field]
                else:
                    count_per_status[item["triage_status"]] = item
        return list(dict(sorted(count_per_status.items())).values())


class MonthlyEvolutionViewSet(StatsViewSet):
    """Generic base ViewSet for monthly finding discovery and fix evolution.

    Provides per-month statistics on finding discoveries, fixes, and the
    running total of active findings. Subclasses configure the finding model
    via filterset_class. False positives are excluded automatically for
    TriageFinding models.

    Attributes:
        serializer_class: Monthly evolution statistics serialization
        pagination_class: Pagination disabled for complete time-series data
        queryset: Set dynamically in get_queryset from filterset_class.Meta.model
        max_months: Maximum number of months returned, capped at 10 years
    """

    serializer_class = FindingsEvolutionStatsSerializer
    pagination_class = None
    queryset = None
    max_months = 120  # 10 years

    def get_queryset(self):
        """Build model-specific queryset with appropriate triage filtering.

        Derives the model from filterset_class.Meta.model and sets self.queryset
        before calling super() so BaseViewSet can apply project membership filtering.
        False positives are excluded when the model extends TriageFinding.

        Returns:
            QuerySet: Project-membership-filtered queryset for the finding model
        """
        model = self.filterset_class.Meta.model
        self.queryset = model.objects.filter(created_from_user_input=False)
        if issubclass(model, TriageFinding):
            self.queryset = self.queryset.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        return super().get_queryset()

    def filter_queryset(self, queryset):
        """Apply filters and compute monthly evolution statistics.

        Runs two aggregation queries (discoveries by first execution month,
        fixes by fixed_date month) then computes a running active total.

        Args:
            queryset: Project-membership-filtered queryset from get_queryset

        Returns:
            List of the most recent monthly data points (up to max_months) with
            discovered, fixed, and active counts
        """
        queryset = super().filter_queryset(queryset)
        discovered_by_month = {
            item["month"]: item["discovered"]
            for item in queryset.annotate(month=TruncMonth(Min("executions__start")))
            .values("month")
            .annotate(discovered=Count("id", distinct=True))
            .order_by("month")
            if item["month"]
        }
        fixed_by_month = {
            item["month"]: item["fixed"]
            for item in queryset.filter(is_fixed=True, fixed_date__isnull=False)
            .annotate(month=TruncMonth("fixed_date"))
            .values("month")
            .annotate(fixed=Count("id", distinct=True))
            .order_by("month")
            if item["month"]
        }
        event_months = sorted(set(discovered_by_month) | set(fixed_by_month))
        if not event_months:
            return []
        now = datetime.datetime.now(tz=event_months[0].tzinfo)
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        active = 0
        result = []
        month = event_months[0]
        while month <= current_month:
            discovered = discovered_by_month.get(month, 0)
            fixed = fixed_by_month.get(month, 0)
            active = max(0, active + discovered - fixed)
            result.append({"month": month.date(), "discovered": discovered, "fixed": fixed, "active": active})
            month = (month + datetime.timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return result[-self.max_months :]


class OSINTEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for OSINT finding monthly evolution statistics."""

    filterset_class = OSINTFilter


class HostEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for host finding monthly evolution statistics."""

    filterset_class = HostFilter


class PortEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for port finding monthly evolution statistics."""

    filterset_class = PortFilter


class PathEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for path finding monthly evolution statistics."""

    filterset_class = PathFilter


class TechnologyEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for technology finding monthly evolution statistics."""

    filterset_class = TechnologyFilter


class CredentialEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for credential finding monthly evolution statistics."""

    filterset_class = CredentialFilter


class VulnerabilityEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for vulnerability finding monthly evolution statistics."""

    filterset_class = VulnerabilityFilter


class ExploitEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for exploit finding monthly evolution statistics."""

    filterset_class = ExploitFilter

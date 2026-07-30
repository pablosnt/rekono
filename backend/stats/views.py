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
from rekono.settings import CONFIG
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
    Restricted to Admin role users.

    Attributes:
        permission_classes (list): Restricts access to Admin role users only.
    """

    permission_classes = [IsAdmin]

    @extend_schema(request=None, responses=RQStatsSerializer)
    def get(self, request: Request) -> Response:
        """Retrieve current statistics for every configured Redis Queue.

        Reads the raw queue statistics from django_rq and narrows each queue's
        entry down to the job and worker count fields exposed by
        RQStatsSerializer, keyed by queue name.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: HTTP 200 with per-queue job and worker statistics.
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
        queryset (QuerySet): Unfixed hosts grouped by os_type with a distinct count
            annotation.
        ordering (list): Most common os_type values first, then alphabetically.
        serializer_class (Serializer): Serializer for host OS-type statistics.
        filterset_class (FilterSet): Filter class for host queryset filtering.
        pagination_class (type | None): Pagination disabled to return the complete
            statistics set.
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
        queryset (QuerySet): Unfixed hosts annotated with open and fixed vulnerability
            counts, plus one count per severity level restricted to open vulnerabilities.
            Each count is a correlated subquery matching vulnerabilities associated with
            the host either directly through a port or through a technology on one of
            its ports, excluding false positives and findings created from user input.
        ordering (list): Hosts with the most open vulnerabilities first, then by fixed
            count, then by each severity count from critical to info, with id as the
            final tiebreaker.
        serializer_class (Serializer): Serializer for host vulnerability statistics.
        filterset_class (FilterSet): Filter class for host queryset filtering.
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
        queryset (QuerySet): Unfixed ports with a known, non-empty service, protocol,
            and port number, grouped by that (service, protocol, port) combination with
            a distinct count annotation.
        ordering (list): Most common combination first, then alphabetically by service,
            port, and protocol.
        serializer_class (Serializer): Serializer for port and service statistics.
        filterset_class (FilterSet): Filter class for port queryset filtering.
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
        queryset (QuerySet): Unfixed technologies not created from user input, grouped by
            name with a distinct count annotation.
        ordering (list): Most common technology names first, then alphabetically.
        serializer_class (Serializer): Serializer for technology statistics.
        filterset_class (FilterSet): Filter class for technology queryset filtering.
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
        queryset (QuerySet): Non-user-created vulnerabilities with a CVE identifier,
            excluding false positives, annotated with each vulnerability's own reference
            (as ``link``) and severity (as ``severity_value``), then grouped by
            (cve, severity_value, link) with open and fixed counts computed per group.
        ordering (list): Groups with the most open vulnerabilities first, then by
            severity_value, then alphabetically by cve.
        serializer_class (Serializer): Serializer for CVE-grouped vulnerability statistics.
        filterset_class (FilterSet): Filter class for vulnerability queryset filtering.
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

    Attributes:
        queryset (QuerySet): Non-user-created vulnerabilities with at least one CWE,
            excluding false positives, grouped by a single CWE value extracted from the
            cwes JSON array with open and fixed counts computed per group.
        ordering (list): Groups with the most open vulnerabilities first, then
            alphabetically by cwe.
        serializer_class (Serializer): Serializer for CWE-grouped vulnerability statistics.
        filterset_class (FilterSet): Filter class for vulnerability queryset filtering.
    """

    # cwes[-1] (last element) is the intended grouping key: CWEs are sorted by
    # numeric value on save, so the last entry has the highest CWE number.
    # PostgreSQL supports negative JSON array indices ($[-1]); SQLite (used in
    # tests) does not. In tests all cwes lists have exactly one element, so
    # cwes[0] and cwes[-1] are equivalent there, which is why CONFIG.testing
    # picks the index to use.
    queryset = (
        Vulnerability.objects.filter(created_from_user_input=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(cwes=None)
        .exclude(cwes=[])
        .annotate(cwe=F(f"cwes__{0 if CONFIG.testing else -1}"))
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
        queryset (QuerySet): Non-user-created vulnerabilities excluding false positives
            and vulnerabilities marked as won't-fix, grouped by severity with open and
            fixed counts computed per group.
        ordering (list): Most severe severity level first.
        serializer_class (Serializer): Serializer for severity-grouped vulnerability
            statistics.
        filterset_class (FilterSet): Filter class for vulnerability queryset filtering.
        pagination_class (type | None): Pagination disabled to return the complete
            severity breakdown.
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
        queryset (QuerySet): Open, non-user-created vulnerabilities excluding false
            positives, annotated with whether at least one Exploit references them and
            grouped by that flag with a distinct count.
        serializer_class (Serializer): Serializer for exploit coverage statistics.
        filterset_class (FilterSet): Filter class for vulnerability queryset filtering.
        pagination_class (type | None): Pagination disabled to return the complete
            coverage overview.
        ordering (list): Vulnerabilities without exploits first, then vulnerabilities
            with exploits.
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
        queryset (QuerySet): All OSINT records. Only used to satisfy the ViewSet's model
            and schema requirements; filter_queryset() ignores it and computes the
            actual statistics itself.
        serializer_class (Serializer): Serializer for triage status statistics.
        filterset_class (FilterSet): OSINTFilter. filter_queryset() temporarily
            reassigns this to each finding type's filter class in turn.
        pagination_class (type | None): Pagination disabled to return the complete
            triage overview.
    """

    queryset = OSINT.objects.all()
    serializer_class = TriagingStatsSerializer
    filterset_class = OSINTFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        """Aggregate triage status counts across every triage-tracked finding type.

        For each finding type (OSINT, Credential, Vulnerability, Exploit) this builds a
        queryset restricted to the projects the requesting user belongs to and grouped by
        triage_status with open and fixed counts, applies that type's filterset by
        temporarily swapping self.filterset_class, and merges the resulting counts into a
        single dict keyed by triage_status. The ``queryset`` argument itself is not used.

        Args:
            queryset (QuerySet): Unused; present to match the ViewSet.filter_queryset
                signature.

        Returns:
            list: Aggregated open and fixed counts per triage_status, sorted by
                triage_status.
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
                model.objects.filter(
                    created_from_user_input=False,
                    # Read authorization based on project membership
                    **{f"{model._project_field}__members": self.request.user},
                )
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
        serializer_class (Serializer): Serializer for monthly finding evolution
            statistics.
        pagination_class (type | None): Pagination disabled to return the complete
            time series.
        queryset (QuerySet | None): None on the class; get_queryset() assigns it from
            filterset_class.Meta.model before returning.
        max_months (int): Maximum number of months returned by filter_queryset().
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
            QuerySet: Project-membership-filtered queryset for the finding model.
        """
        model = self.filterset_class.Meta.model
        self.queryset = model.objects.filter(created_from_user_input=False)
        if issubclass(model, TriageFinding):
            self.queryset = self.queryset.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        return super().get_queryset()

    def filter_queryset(self, queryset):
        """Apply filters and compute monthly finding evolution statistics.

        Runs two aggregation queries on the filtered queryset: discoveries grouped by
        the month of each finding's earliest execution start, and fixes grouped by the
        month of fixed_date (only for findings that are fixed and have a fixed_date).
        Findings with no execution start month are excluded from the discovered count.
        The two month-to-count maps are then walked together, month by month, from the
        first month with any activity through the current month, filling in a zero
        count for any month with no activity, and accumulating a running active total
        as max(0, previous active + discovered - fixed).

        Args:
            queryset (QuerySet): Project-membership-filtered queryset from
                get_queryset().

        Returns:
            list: One entry per month from the first active month through the current
                month, each with month, discovered, fixed, and active counts, truncated
                to the most recent max_months entries. Empty if there is no discovered
                or fixed activity at all.
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
    """ViewSet for OSINT finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): OSINTFilter. get_queryset() reads its Meta.model
            to target the OSINT model for this evolution view.
    """

    filterset_class = OSINTFilter


class HostEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for host finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): HostFilter. get_queryset() reads its Meta.model
            to target the Host model for this evolution view.
    """

    filterset_class = HostFilter


class PortEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for port finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): PortFilter. get_queryset() reads its Meta.model
            to target the Port model for this evolution view.
    """

    filterset_class = PortFilter


class PathEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for path finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): PathFilter. get_queryset() reads its Meta.model
            to target the Path model for this evolution view.
    """

    filterset_class = PathFilter


class TechnologyEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for technology finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): TechnologyFilter. get_queryset() reads its
            Meta.model to target the Technology model for this evolution view.
    """

    filterset_class = TechnologyFilter


class CredentialEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for credential finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): CredentialFilter. get_queryset() reads its
            Meta.model to target the Credential model for this evolution view.
    """

    filterset_class = CredentialFilter


class VulnerabilityEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for vulnerability finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): VulnerabilityFilter. get_queryset() reads its
            Meta.model to target the Vulnerability model for this evolution view.
    """

    filterset_class = VulnerabilityFilter


class ExploitEvolutionViewSet(MonthlyEvolutionViewSet):
    """ViewSet for exploit finding monthly evolution statistics.

    Attributes:
        filterset_class (FilterSet): ExploitFilter. get_queryset() reads its Meta.model
            to target the Exploit model for this evolution view.
    """

    filterset_class = ExploitFilter

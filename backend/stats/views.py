"""Viewsets of the statistics endpoints.

Each viewset defines the aggregation that answers one question about the findings,
and the base viewset takes care of applying the filters of that finding type and of
keeping only the projects that the user belongs to.
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
    """Read the state of the background job queues.

    Attributes:
        permission_classes: Only the admins, since the queues are about the whole
          deployment instead of about one project.
    """

    permission_classes = [IsAdmin]

    @extend_schema(request=None, responses=RQStatsSerializer)
    def get(self, request: Request) -> Response:
        """Get the jobs and the workers of each queue.

        Args:
            request: Request that asks for the statistics, whose data isn't read
              because they cover the whole deployment.

        Returns:
            The statistics of every queue, keyed by its name, with only the job and
            worker counts of the many fields that RQ reports.
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
    """Read how many hosts run each operating system.

    Attributes:
        queryset: Hosts that are still there, grouped by operating system family.
        ordering: The most common operating systems first.
        serializer_class: Serializer of the host statistics.
        filterset_class: Filters of the hosts.
        pagination_class: No pagination, since there are only a few families.
    """

    queryset = Host.objects.filter(is_fixed=False).values("os_type").annotate(count=Count("id", distinct=True))
    ordering = ["-count", "os_type"]
    serializer_class = HostStatsSerializer
    filterset_class = HostFilter
    pagination_class = None


class HostVulnerabilitiesStatsViewSet(StatsViewSet):
    """Read how many vulnerabilities were found in each host.

    Attributes:
        queryset: Hosts that are still there, with the vulnerabilities found in
          them, counted by status and by severity. The vulnerabilities are reached
          through the port and through the technologies of that port, so a host
          counts everything that was found in it no matter how deep it is.
        ordering: The most vulnerable hosts first.
        serializer_class: Serializer of the host vulnerability statistics.
        filterset_class: Filters of the hosts.
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
    """Read how many times each service is exposed.

    Attributes:
        queryset: Ports that are still there and whose service is known, grouped by
          service, protocol, and port number.
        ordering: The most exposed services first.
        serializer_class: Serializer of the port statistics.
        filterset_class: Filters of the ports.
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
    """Read how many times each technology was found.

    Attributes:
        queryset: Technologies that are still there and that no user created,
          grouped by name.
        ordering: The most used technologies first.
        serializer_class: Serializer of the technology statistics.
        filterset_class: Filters of the technologies.
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
    """Read how many times each CVE was found.

    Attributes:
        queryset: Vulnerabilities with a CVE that the auditors didn't discard and
          that no user created, grouped by CVE with their severity and advisory.
        ordering: The most repeated and most severe CVEs first.
        serializer_class: Serializer of the CVE statistics.
        filterset_class: Filters of the vulnerabilities.
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
    """Read how many vulnerabilities belong to each weakness.

    Attributes:
        queryset: Vulnerabilities with a CWE that the auditors didn't discard and
          that no user created, grouped by their most specific CWE.
        ordering: The most repeated weaknesses first.
        serializer_class: Serializer of the CWE statistics.
        filterset_class: Filters of the vulnerabilities.
    """

    # The CWEs are sorted by number when they are saved, so the last one is the most specific.
    # PostgreSQL supports negative JSON array indices, but SQLite, which is used in the tests,
    # doesn't, and there every vulnerability has only one CWE
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
    """Read how many vulnerabilities of each severity are fixed.

    Attributes:
        queryset: Vulnerabilities that the auditors didn't discard and that no user
          created, grouped by severity.
        ordering: The most severe vulnerabilities first.
        serializer_class: Serializer of the severity statistics.
        filterset_class: Filters of the vulnerabilities.
        pagination_class: No pagination, since there are only a few severities.
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
    """Read how many vulnerabilities have a public exploit.

    Attributes:
        queryset: Vulnerabilities that are still there and that the auditors didn't
          discard, grouped by whether an exploit was found for them.
        serializer_class: Serializer of the exploit coverage statistics.
        filterset_class: Filters of the vulnerabilities.
        pagination_class: No pagination, since there are only two groups.
        ordering: The vulnerabilities without exploits first.
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
    """Read how many findings are in each triage status.

    Attributes:
        queryset: The OSINT findings, only to give the viewset a model, since the
          statistics are calculated from all the finding types that are triaged.
        serializer_class: Serializer of the triage statistics.
        filterset_class: Filters of the OSINT findings, replaced by the ones of each
          finding type while the statistics are calculated.
        pagination_class: No pagination, since there are only a few statuses.
    """

    queryset = OSINT.objects.all()
    serializer_class = TriagingStatsSerializer
    filterset_class = OSINTFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        """Count the findings of every triaged type, grouped by their triage status.

        Args:
            queryset: Not used, since each finding type needs its own query.

        Returns:
            The number of findings in each triage status, with the ones that are
            fixed counted apart from the ones that are still there.
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
    """Base viewset to read how the findings of one type evolved over the months.

    The finding type comes from the model of the filters, so each subclass only
    defines them.

    Attributes:
        serializer_class: Serializer of the evolution statistics.
        pagination_class: No pagination, since the whole series is one chart.
        queryset: Built from the filters when the request is answered.
        max_months: Months that the series can cover at most.
    """

    serializer_class = FindingsEvolutionStatsSerializer
    pagination_class = None
    queryset = None
    max_months = 120  # 10 years

    def get_queryset(self):
        """Get the findings of the type that this viewset reports about.

        Returns:
            The findings that no user created, without the ones that the auditors
            discarded if the finding type can be triaged.
        """
        model = self.filterset_class.Meta.model
        self.queryset = model.objects.filter(created_from_user_input=False)
        if issubclass(model, TriageFinding):
            self.queryset = self.queryset.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        return super().get_queryset()

    def filter_queryset(self, queryset):
        """Count how many findings were discovered and fixed during each month.

        Args:
            queryset: Findings to be counted, already scoped to the finding type
              that the viewset serves.

        Returns:
            One entry per month, from the first month with activity to the current
            one, with the findings that were still there when each month ended.
            The months without activity are included too, so the series has no
            holes, and it's empty when nothing was ever discovered or fixed.
        """
        queryset = super().filter_queryset(queryset)
        # A finding is discovered when the first execution that reported it started, so the
        # findings created before any execution started are left out of the series
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
            # Adding 32 days and going back to the first day always lands on the next month
            month = (month + datetime.timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return result[-self.max_months :]


class OSINTEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the data found on public sources evolved over the months.

    Attributes:
        filterset_class: Filters of the OSINT findings, which are the ones reported.
    """

    filterset_class = OSINTFilter


class HostEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the hosts found in the network evolved over the months.

    Attributes:
        filterset_class: Filters of the hosts, which are the ones reported.
    """

    filterset_class = HostFilter


class PortEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the ports found in the hosts evolved over the months.

    Attributes:
        filterset_class: Filters of the ports, which are the ones reported.
    """

    filterset_class = PortFilter


class PathEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the paths found in the ports evolved over the months.

    Attributes:
        filterset_class: Filters of the paths, which are the ones reported.
    """

    filterset_class = PathFilter


class TechnologyEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the technologies found in the ports evolved over the months.

    Attributes:
        filterset_class: Filters of the technologies, which are the ones reported.
    """

    filterset_class = TechnologyFilter


class CredentialEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the exposed credentials evolved over the months.

    Attributes:
        filterset_class: Filters of the credentials, which are the ones reported.
    """

    filterset_class = CredentialFilter


class VulnerabilityEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the vulnerabilities evolved over the months.

    Attributes:
        filterset_class: Filters of the vulnerabilities, which are the ones reported.
    """

    filterset_class = VulnerabilityFilter


class ExploitEvolutionViewSet(MonthlyEvolutionViewSet):
    """Read how the exploits found evolved over the months.

    Attributes:
        filterset_class: Filters of the exploits, which are the ones reported.
    """

    filterset_class = ExploitFilter

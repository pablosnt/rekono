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
    permission_classes = [IsAdmin]

    @extend_schema(request=None, responses=RQStatsSerializer)
    def get(self, request: Request) -> Response:
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
    ordering_fields = []
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]


class LatestViewSet(StatsViewSet):
    top_items = 5
    pagination_class = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset[: self.top_items]


class LatestTasksViewSet(LatestViewSet):
    queryset = Task.objects.exclude(start=None)
    ordering = ["-start"]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter


class LatestHostsViewSet(LatestViewSet):
    queryset = Host.objects.filter(is_fixed=False).annotate(latest=Max("executions__start"))
    ordering = ["-latest"]
    serializer_class = HostSerializer
    filterset_class = HostFilter


class LatestVulnerabilitiesViewSet(LatestViewSet):
    queryset = (
        Vulnerability.objects.filter(is_fixed=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .annotate(latest=Max("executions__start"))
    )
    ordering = ["-latest"]
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter


class TopProjectsViewSet(LatestViewSet):
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
    queryset = Host.objects.filter(is_fixed=False).values("os_type").annotate(count=Count("os_type"))
    ordering = ["-count", "os_type"]
    serializer_class = HostStatsSerializer
    filterset_class = HostFilter
    pagination_class = None


class HostVulnerabilitiesStatsViewSet(StatsViewSet):
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
    queryset = (
        Port.objects.filter(is_fixed=False).values("service", "protocol", "port").annotate(count=Count("service"))
    )
    ordering = ["-count", "service", "port", "protocol"]
    serializer_class = PortStatsSerializer
    filterset_class = PortFilter


class TechnologyStatsViewSet(StatsViewSet):
    queryset = Technology.objects.filter(is_fixed=False).values("name").annotate(count=Count("name"))
    ordering = ["-count", "name"]
    serializer_class = TechnologyStatsSerializer
    filterset_class = TechnologyFilter


class VulnerabilityTrendingStatsViewSet(StatsViewSet):
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
    queryset = (
        OSINT.objects.values("triage_status")
        .annotate(open=Count("id", distinct=True, filter=Q(is_fixed=False)))
        .annotate(fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
    )
    ordering = []
    serializer_class = TriagingStatsSerializer
    filterset_class = OSINTFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # This is needed because it's not possible no union multiple querysets
        # and then, get counts grouped by triage_status
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

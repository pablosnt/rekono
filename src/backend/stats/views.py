from django.db.models import Count, ExpressionWrapper, F, FloatField, Max, OuterRef, Q
from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from findings.enums import Severity, TriageStatus
from findings.filters import HostFilter, PortFilter, TechnologyFilter, VulnerabilityFilter
from findings.framework.filters import TriageFindingFilter
from findings.models import OSINT, Credential, Exploit, Host, Port, Technology, Vulnerability
from findings.serializers import HostSerializer
from framework.views import BaseViewSet
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectSerializer
from security.authorization.permissions import IsAdmin
from stats.serializers import (
    EvolutionStatsSerializer,
    HostStatsSerializer,
    HostVulnerabilitiesStatsSerializer,
    PortStatsSerializer,
    RQStatsSerializer,
    TechnologyStatsSerializer,
    TriagingStatsSerializer,
    VulnerabilityCVEStatsSerializer,
    VulnerabilityCWEStatsSerializer,
    VulnerabilityFixProgressPerSeverityStatsSerializer,
    VulnerabilityFixProgressStatsSerializer,
    VulnerabilitySeverityStatsSerializer,
)
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.serializers import TaskSerializer

# TODO: Review what of these stats must be limited to the first X top items
top_items = 5


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


# TODO: Adapt frontend to multiple endpoints approach
class LatestTasksViewSet(StatsViewSet):
    queryset = Task.objects.exclude(start=None).order_by("-start")[:top_items]
    serializer_class = TaskSerializer
    filterset_class = TaskFilter


class LatestHostsViewSet(StatsViewSet):
    queryset = (
        Host.objects.filter(is_fixed=False).annotate(latest=Max("executions__start")).order_by("-latest")[:top_items]
    )
    serializer_class = HostSerializer
    filterset_class = HostFilter


class LatestVulnerabilitiesViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.filter(is_fixed=False)
        .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .annotate(latest=Max("executions__start"))
        .order_by("-latest")[:top_items]
    )
    serializer_class = HostSerializer
    filterset_class = HostFilter


class TopProjectsViewSet(StatsViewSet):
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
        .order_by(
            "-vulnerabilities_count",
            "-hosts_count",
            "-tasks_count",
            "-targets_count",
        )[:top_items]
    )
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter


class HostStatsViewSet(StatsViewSet):
    queryset = Host.objects.filter(is_fixed=False).values("os_type").annotate(count=Count("os_type")).order_by("-count")
    serializer_class = HostStatsSerializer
    filterset_class = ProjectFilter


class HostVulnerabilitiesStatsViewSet(StatsViewSet):
    queryset = (
        Host.objects.filter(is_fixed=False)
        .annotate(
            vulnerabilities=Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            .filter(Q(port__host__pk=OuterRef("id")) | Q(technology__port__host__pk=OuterRef("id")))
            .values("port__host", "technology__port__host")
            .annotate(fixed=Count("id", filter=Q(is_fixed=True)), open=Count("id", filter=Q(is_fixed=False)))
            .order_by("-open", "-fixed")
            .first(),
            vulnerabilities_per_severity=Vulnerability.objects.exclude(is_fixed=True)
            .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            .filter(Q(port__host__pk=OuterRef("id")) | Q(technology__port__host__pk=OuterRef("id")))
            .values("port__host", "technology__port__host")
            .values("severity")
            .annotate(**{severity.name: Count("id", filter=Q(severity=severity)) for severity in Severity})
            .order_by("-critical", "-high", "-medium", "-low", "-info")
            .first(),
        )
        .values("id", "ip", "domain", "vulnerabilities", "vulnerabilities_per_severity")
        .order_by("-vulnerabilities")
    )
    serializer_class = HostVulnerabilitiesStatsSerializer
    filterset_class = ProjectFilter


class HostEvolutionStatsViewSet(StatsViewSet):
    queryset = (
        Host.objects.prefetch_related("executions")
        .values("executions__start")
        .annotate(count=Count("executions__start", distinct=True))
        .annotate(date=F("executions__start"))
        .order_by("date")
    )
    serializer_class = EvolutionStatsSerializer
    filterset_class = HostFilter


class PortStatsViewSet(StatsViewSet):
    queryset = (
        Port.objects.filter(is_fixed=False)
        .values("service", "protocol", "port")
        .annotate(count=Count("service"))
        .order_by("-count")
    )
    serializer_class = PortStatsSerializer
    filterset_class = PortFilter


class TechnologyStatsViewSet(StatsViewSet):
    queryset = Technology.objects.filter(is_fixed=False).values("name").annotate(count=Count("name")).order_by("-count")
    serializer_class = TechnologyStatsSerializer
    filterset_class = TechnologyFilter


class VulnerabilityTrendingStatsViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .filter(trending=True)
        .exclude(cve=None)
        .annotate(link=Max("reference"))
        .annotate(severity_value=Max("severity"))
        .values("cve", "severity_value", "link")
        .annotate(open=Count("cve", filter=Q(is_fixed=False)), fixed=Count("cve", filter=Q(is_fixed=True)))
        .order_by("-open")
    )
    serializer_class = VulnerabilityCVEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityCVEStatsViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(cve=None)
        .annotate(link=Max("reference"))
        .annotate(severity_value=Max("severity"))
        .values("cve", "severity_value", "link")
        .annotate(open=Count("cve", filter=Q(is_fixed=False)), fixed=Count("cve", filter=Q(is_fixed=True)))
        .order_by("-open")[:top_items]
    )
    serializer_class = VulnerabilityCVEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityCWEStatsViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(cwe=None)
        .values("cwe")
        .annotate(open=Count("cwe", filter=Q(is_fixed=False)), fixed=Count("cwe", filter=Q(is_fixed=True)))
        .order_by("-open")[:top_items]
    )
    serializer_class = VulnerabilityCWEStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilitySeverityStatsViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .values("severity")
        .annotate(open=Count("severity", filter=Q(is_fixed=False)), fixed=Count("severity", filter=Q(is_fixed=True)))
        .order_by("-severity")
    )
    serializer_class = VulnerabilitySeverityStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityEvolutionStatsViewSet(StatsViewSet):
    queryset = (
        Host.objects.prefetch_related("executions")
        .values("executions__start", "severity")
        .annotate(count=Count("executions__start", distinct=True))
        .annotate(date=F("executions__start"))
        .order_by("date", "-severity")
    )
    serializer_class = EvolutionStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityFixProgressStatsViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .annotate(
            open=Count("id", distinct=True, filter=Q(is_fixed=True)),
            fixed=Count("id", distinct=True, filter=Q(is_fixed=True)),
        )
        .annotate(
            progress=ExpressionWrapper((F("fixed") * 1.0 / (F("open") + F("fixed"))) * 100, output_field=FloatField())
        )
        .order_by("-severity")
    )
    serializer_class = VulnerabilityFixProgressStatsSerializer
    filterset_class = VulnerabilityFilter


class VulnerabilityFixProgressPerServerityStatsViewSet(StatsViewSet):
    queryset = (
        Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
        .exclude(triage_status=TriageStatus.WONT_FIX)
        .values("severity")
        .annotate(
            open=Count("id", distinct=True, filter=Q(is_fixed=True)),
            fixed=Count("id", distinct=True, filter=Q(is_fixed=True)),
        )
        .annotate(
            progress=ExpressionWrapper((F("fixed") * 1.0 / (F("open") + F("fixed"))) * 100, output_field=FloatField())
        )
        .order_by("-severity")
    )
    serializer_class = VulnerabilityFixProgressPerSeverityStatsSerializer
    filterset_class = VulnerabilityFilter


class TriagingStatsViewSet(StatsViewSet):
    # TODO: fp_rate removed. It can be calculated based on the distribution
    queryset = (
        OSINT.objects.values("triage_status")
        .annotate(count=Count("id", distinct=True))
        .order_by("-count")
        .union(
            Credential.objects.values("triage_status").annotate(count=Count("id", distinct=True)).order_by("-count"),
            Vulnerability.objects.values("triage_status").annotate(count=Count("id", distinct=True)).order_by("-count"),
            Exploit.objects.values("triage_status").annotate(count=Count("id", distinct=True)).order_by("-count"),
        )
        .values("triage_status")
        .annotate(
            open=Count("id", distinct=True, filter=Q(is_fixed=False)),
            fixed=Count("id", distinct=True, filter=Q(is_fixed=True)),
        )
        .order_by("-open")
    )
    serializer_class = TriagingStatsSerializer
    # TODO: Test this. TriageFindingFilter is linked to the OSINT model, so it might not work in a union queryset
    filterset_class = TriageFindingFilter

from typing import Any

from django.db.models import Count, F, Max, Q
from django_rq.utils import get_statistics
from drf_spectacular.utils import extend_schema, inline_serializer
from findings.enums import Severity, TriageStatus
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Port,
    Technology,
    Vulnerability,
)
from findings.serializers import HostSerializer, VulnerabilitySerializer
from framework.views import StatsView
from projects.models import Project
from projects.serializers import ProjectSerializer
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from security.authorization.permissions import IsAdmin
from stats.serializers import ScopeSerializer, ScopeTimelineSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer

rq_fields = {
    field: serializers.IntegerField()
    for field in [
        "jobs",  # Enqueued jobs
        "workers",
        "finished_jobs",
        "started_jobs",  # Running jobs
        "deferred_jobs",
        "failed_jobs",
        "scheduled_jobs",
    ]
}


class RQStatsView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="RQStats",
                fields={
                    "tasks": inline_serializer(name="TasksStats", fields=rq_fields),
                    "executions": inline_serializer(
                        name="ExecutionsStats", fields=rq_fields
                    ),
                    "findings": inline_serializer(
                        name="FindingsStats", fields=rq_fields
                    ),
                    "monitor": inline_serializer(name="MonitorStats", fields=rq_fields),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        stats: dict[str, dict[str, Any]] = {
            "tasks": {},
            "executions": {},
            "findings": {},
            "monitor": {},
        }
        for queue in get_statistics().get("queues", []):
            stats[queue["name"]] = {k: v for k, v in queue.items() if k in rq_fields}
        return Response(stats, status=HTTP_200_OK)


# TODO: Performance
class ActivityStatsView(StatsView):

    def _stats(self, request: Request, data: dict[str, Any]) -> dict[str, Any]:
        stats = {
            "latest_tasks": TaskSerializer(
                self._filter(
                    request, Task.objects.exclude(start=None).order_by("-start"), data
                )[: self.top],
                many=True,
            ).data,
            "latest_hosts": HostSerializer(
                self._filter(
                    request,
                    Host.objects.filter(is_fixed=False)
                    .annotate(max_start=Max("executions__start"))
                    .order_by("-max_start"),
                    data,
                )[: self.top],
                many=True,
            ).data,
            "latest_vulnerabilities": VulnerabilitySerializer(
                self._filter(
                    request,
                    Vulnerability.objects.filter(is_fixed=False)
                    .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                    .annotate(max_start=Max("executions__start"))
                    .order_by("-max_start"),
                    data,
                )[: self.top],
                many=True,
            ).data,
        }
        if not data.get("project") and not data.get("target"):
            stats["top_projects"] = ProjectSerializer(
                self._filter(
                    request,
                    Project.objects.all()
                    .annotate(targets_count=Count("targets", distinct=True))
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
                            filter=~Q(
                                targets__tasks__executions__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE
                            )
                            & Q(
                                targets__tasks__executions__vulnerability__is_fixed=False
                            ),
                        )
                    )
                    .order_by(
                        "-vulnerabilities_count",
                        "-hosts_count",
                        "-tasks_count",
                        "-targets_count",
                    ),
                    data,
                )[: self.top],
                many=True,
            ).data
        return stats

    @extend_schema(
        request=ScopeSerializer,
        responses={
            200: inline_serializer(
                name="LatestActivityStats",
                fields={
                    "latest_tasks": TaskSerializer(many=True),
                    "latest_hosts": HostSerializer(many=True),
                    "latest_vulnerabilities": VulnerabilitySerializer(many=True),
                    "top_projects": ProjectSerializer(many=True),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        return super().get(request)


class AssetsStatsView(StatsView):

    def _stats(self, request: Request, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "top_vulnerabilities": self._filter(
                request,
                Host.objects.annotate(
                    fixed_port_vulnerability=Count(
                        "port__vulnerability",
                        distinct=True,
                        filter=~Q(
                            port__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE
                        )
                        & Q(port__vulnerability__is_fixed=True),
                    ),
                    fixed_technology_vulnerability=Count(
                        "port__technology__vulnerability",
                        distinct=True,
                        filter=~Q(
                            port__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE
                        )
                        & Q(port__vulnerability__is_fixed=True),
                    ),
                )
                .annotate(
                    **{
                        k: v
                        for item in [
                            {
                                f"port_vulnerability_{severity.value.lower()}": Count(
                                    "port__vulnerability",
                                    distinct=True,
                                    filter=~Q(
                                        port__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE
                                    )
                                    & Q(port__vulnerability__is_fixed=False)
                                    & Q(port__vulnerability__severity=severity),
                                ),
                                f"technology_vulnerability_{severity.value.lower()}": Count(
                                    "port__technology__vulnerability",
                                    distinct=True,
                                    filter=~Q(
                                        port__vulnerability__triage_status=TriageStatus.FALSE_POSITIVE
                                    )
                                    & Q(port__vulnerability__is_fixed=False)
                                    & Q(port__vulnerability__severity=severity),
                                ),
                            }
                            for severity in Severity
                        ]
                        for k, v in item.items()
                    }
                )
                .annotate(
                    **{
                        k: v
                        for item in [
                            {
                                f"vulnerabilities_{severity.value.lower()}": F(
                                    f"port_vulnerability_{severity.value.lower()}"
                                )
                                + F(
                                    f"technology_vulnerability_{severity.value.lower()}"
                                )
                            }
                            for severity in Severity
                        ]
                        for k, v in item.items()
                    }
                )
                .annotate(
                    vulnerabilities=sum(
                        [
                            F(f"vulnerabilities_{severity.value.lower()}")
                            for severity in Severity
                        ]
                    ),
                    fixed_vulnerabilities=F("fixed_port_vulnerability")
                    + F("fixed_technology_vulnerability"),
                )
                .values(
                    "id",
                    "address",
                    "fixed_vulnerabilities",
                    "vulnerabilities",
                    *[
                        f"vulnerabilities_{severity.value.lower()}"
                        for severity in Severity
                    ],
                )
                .order_by("-vulnerabilities", "-fixed_vulnerabilities"),
                data,
            )[: self.top],
            "os_distribution": self._filter(
                request,
                Host.objects.filter(is_fixed=False)
                .values("os_type")
                .annotate(total=Count("os_type"))
                .order_by("-total"),
                data,
            ),
            "services_distribution": self._filter(
                request,
                Port.objects.filter(is_fixed=False)
                .values("service", "protocol", "port")
                .annotate(total=Count("service"))
                .order_by("-total"),
                data,
            ),
            "technologies_distribution": self._filter(
                request,
                Technology.objects.filter(is_fixed=False)
                .values("name")
                .annotate(total=Count("name"))
                .order_by("-total"),
                data,
            ),
        }

    # TODO: Migrate this to standard serializers. We will save a lot of code lines. Maybe there is a way to get the annotations from the serializer
    @extend_schema(
        request=ScopeSerializer,
        responses={
            200: inline_serializer(
                name="AssetsStats",
                fields={
                    "top_vulnerabilities": inline_serializer(
                        name="TopVulnerabilities",
                        fields={
                            "id": serializers.IntegerField(),
                            "address": serializers.CharField(),
                            "fixed_vulnerabilities": serializers.IntegerField(),
                            "vulnerabilities": serializers.IntegerField(),
                            "vulnerabilities_info": serializers.IntegerField(),
                            "vulnerabilities_low": serializers.IntegerField(),
                            "vulnerabilities_medium": serializers.IntegerField(),
                            "vulnerabilities_high": serializers.IntegerField(),
                            "vulnerabilities_critical": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "os_distribution": inline_serializer(
                        name="OSDistribution",
                        fields={
                            "os": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "services_distribution": inline_serializer(
                        name="ServicesDistribution",
                        fields={
                            "service": serializers.CharField(),
                            "port": serializers.IntegerField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "technologies_distribution": inline_serializer(
                        name="TechnologiesDistribution",
                        fields={
                            "name": serializers.IntegerField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        return super().get(request)


class VulnerabilityStatsView(StatsView):

    def _stats(self, request: Request, data: dict[str, Any]) -> dict[str, Any]:
        vulnerabilities = Vulnerability.objects.exclude(
            triage_status=TriageStatus.FALSE_POSITIVE
        )
        current_vulnerabilities = vulnerabilities.filter(is_fixed=False)
        fixed_vulnerabilities = vulnerabilities.filter(is_fixed=True)
        return {
            "trending_cve": VulnerabilitySerializer(
                self._filter(
                    request, current_vulnerabilities.filter(trending=True), data
                ),
                many=True,
            ).data,
            "top_cve": VulnerabilitySerializer(
                self._filter(
                    request,
                    current_vulnerabilities.exclude(cve=None)
                    .annotate(total=Count("cve"))
                    .order_by("-total"),
                    data,
                )[: self.top],
                many=True,
            ).data,
            "top_fixed_cve": VulnerabilitySerializer(
                self._filter(
                    request,
                    fixed_vulnerabilities.exclude(cve=None)
                    .values("cve")
                    .annotate(total=Count("cve"))
                    .order_by("-total"),
                    data,
                )[: self.top],
                many=True,
            ).data,
            "cwe_distribution": self._filter(
                request,
                current_vulnerabilities.exclude(cwe=None)
                .values("cwe")
                .annotate(total=Count("cwe"))
                .order_by("-total"),
                data,
            ),
            "fixed_cwe_distribution": self._filter(
                request,
                fixed_vulnerabilities.exclude(cwe=None)
                .values("cwe")
                .annotate(total=Count("cwe"))
                .order_by("-total"),
                data,
            ),
            "severity_distribution": self._filter(
                request,
                current_vulnerabilities.values("severity")
                .annotate(total=Count("severity"))
                .order_by("-total"),
                data,
            ),
            "fixed_severity_distribution": self._filter(
                request,
                fixed_vulnerabilities.values("severity")
                .annotate(total=Count("severity"))
                .order_by("-total"),
                data,
            ),
        }

    @extend_schema(
        request=ScopeSerializer,
        responses={
            200: inline_serializer(
                name="VulnerabilitiesStats",
                fields={
                    "trending_cve": VulnerabilitySerializer(many=True),
                    "top_cve": inline_serializer(
                        name="TopCve",
                        fields={
                            "cve": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "top_fixed_cve": inline_serializer(
                        name="TopFixedCve",
                        fields={
                            "cve": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "cwe_distribution": inline_serializer(
                        name="CweDistribution",
                        fields={
                            "cwe": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "fixed_cwe_distribution": inline_serializer(
                        name="FixedCweDistribution",
                        fields={
                            "cwe": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "severity_distribution": inline_serializer(
                        name="SeverityDistribution",
                        fields={
                            "severity": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                    "fixed_severity_distribution": inline_serializer(
                        name="FixedSeverityDistribution",
                        fields={
                            "severity": serializers.CharField(),
                            "total": serializers.IntegerField(),
                        },
                        many=True,
                    ),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        return super().get(request)


class TriagingStatsView(StatsView):

    def _stats(self, request: Request, data: dict[str, Any]) -> dict[str, Any]:
        all = 0
        all_fps = 0
        current = 0
        current_fps = 0
        triage_distribution: dict[str, int] = {}
        for model in [OSINT, Credential, Vulnerability, Exploit]:
            all += self._filter(request, model.objects.all(), data).count()
            all_fps += self._filter(request, model.objects.all(), data).count()
            current += self._filter(
                request,
                model.objects.filter(
                    is_fixed=False, triage_status=TriageStatus.FALSE_POSITIVE
                ),
                data,
            ).count()
            current_fps += self._filter(
                request,
                model.objects.filter(
                    is_fixed=False, triage_status=TriageStatus.FALSE_POSITIVE
                ),
                data,
            ).count()
            triage_distribution.update(
                {
                    i["triage_status"]: triage_distribution.get(i["triage_status"], 0)
                    + i.get("total", 0)
                    for i in self._filter(
                        request,
                        model.objects.filter(is_fixed=False)
                        .values("triage_status")
                        .annotate(total=Count("triage_status"))
                        .order_by("-total"),
                        data,
                    )
                }
            )
        return {
            "fp_rate_all": round((all_fps / all) * 100, 2),
            "fp_rate_not_fixed": round((current_fps / current) * 100),
            "triage_distribution": triage_distribution,
        }

    @extend_schema(
        request=ScopeSerializer,
        responses={
            200: inline_serializer(
                name="TriagingStats",
                fields={
                    "fp_rate_all": serializers.FloatField(),
                    "fp_rate_not_fixed": serializers.FloatField(),
                    "triage_distribution": inline_serializer(
                        name="FixedSeverityDistribution",
                        fields={
                            s.value: serializers.IntegerField() for s in TriageStatus
                        },
                    ),
                },
            )
        },
    )
    def get(self, request: Request) -> Response:
        return super().get(request)


# TODO: Evolution
#   Scans per date (Last year? 1/3/6 Months?)
#   Discoverd assets (host, port/service) per time (Last year? 1/3/6 Months?)
#   Findings per time and type & Vulnerabilities per time and severity ?  (Last year? 1/3/6 Months?)
#   Fixed findings per time & Fixed vulnerabilities per time and severity ?  (Last year? 1/3/6 Months?)

from datetime import date
from typing import Any

from django.db.models import Count, ExpressionWrapper, F
from django.db.models import FloatField as Float
from django.db.models import Max, Min, Q, QuerySet
from django.db.models.functions import TruncDate
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
from framework.models import BaseModel
from projects.models import Project
from projects.serializers import ProjectSerializer
from rest_framework.serializers import (
    CharField,
    DateField,
    FloatField,
    IntegerField,
    Serializer,
    SerializerMethodField,
)
from stats.framework.serializers import StatsSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer


class QueueStats(Serializer):
    jobs = IntegerField()
    workers = IntegerField()
    finished_jobs = IntegerField()
    started_jobs = IntegerField()
    deferred_jobs = IntegerField()
    failed_jobs = IntegerField()
    scheduled_jobs = IntegerField()


class OSCount(Serializer):
    os_type = CharField()
    count = IntegerField()


class PortCount(Serializer):
    port = IntegerField()
    protocol = CharField()
    service = CharField()
    count = IntegerField()


class TechnologyCount(Serializer):
    name = CharField()
    count = IntegerField()


class DateCount(Serializer):
    date = DateField()
    count = IntegerField()


class CveCount(Serializer):
    cve = CharField()
    severity_value = CharField()
    link = CharField()
    count = IntegerField()


class CweCount(Serializer):
    cwe = CharField()
    count = IntegerField()


class SeverityProgress(Serializer):
    severity = CharField()
    progress = FloatField()


class SeverityCount(Serializer):
    severity = CharField()
    count = IntegerField()


class DateSeverityCount(DateCount, SeverityCount):
    pass


class HostVulnerabilities(Serializer):
    id = IntegerField()
    address = CharField()
    vulnerabilities = IntegerField()
    vulnerabilities_per_severity = SeverityCount(many=True)
    fixed_vulnerabilities = IntegerField()


class TriageStatusCount(Serializer):
    status = CharField()
    count = IntegerField()


class RQStatsSerializer(Serializer):
    tasks = QueueStats()
    executions = QueueStats()
    findings = QueueStats()
    monitor = QueueStats()


class ActivityStatsSerializer(StatsSerializer):
    latest_tasks = SerializerMethodField(read_only=True)
    latest_hosts = SerializerMethodField(read_only=True)
    latest_vulnerabilities = SerializerMethodField(read_only=True)
    top_projects = SerializerMethodField(read_only=True)

    def get_latest_tasks(self, instance: Any) -> TaskSerializer(many=True):
        return self._serialize(
            TaskSerializer,
            self._get_queryset(Task).exclude(start=None).order_by("-start")[: self.top],
        )

    def get_latest_hosts(self, instance: Any) -> HostSerializer(many=True):
        return self._serialize(
            HostSerializer,
            self._get_queryset(Host)
            .filter(is_fixed=False)
            .annotate(max_start=Max("executions__start"))
            .order_by("-max_start")[: self.top],
        )

    def get_latest_vulnerabilities(
        self, instance: Any
    ) -> VulnerabilitySerializer(many=True):
        return self._serialize(
            VulnerabilitySerializer,
            self._get_queryset(Vulnerability)
            .filter(is_fixed=False)
            .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            .annotate(latest=Max("executions__start"))
            .order_by("-latest")[: self.top],
        )

    def get_top_projects(self, instance: Any) -> ProjectSerializer(many=True):
        return self._serialize(
            ProjectSerializer,
            (
                self._get_queryset(Project)
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
                        & Q(targets__tasks__executions__vulnerability__is_fixed=False),
                    )
                )
                .order_by(
                    "-vulnerabilities_count",
                    "-hosts_count",
                    "-tasks_count",
                    "-targets_count",
                )[: self.top]
                if self.validated_data.get("project") is None
                and self.validated_data.get("target") is None
                else Project.objects.none()
            ),
        )


class HostsStatsSerializer(StatsSerializer):
    top_vulnerable = SerializerMethodField(read_only=True)
    os_distribution = SerializerMethodField(read_only=True)
    services_distribution = SerializerMethodField(read_only=True)
    technologies_distribution = SerializerMethodField(read_only=True)
    model = Host

    def get_top_vulnerable(self, instance: Any) -> HostVulnerabilities(many=True):
        queryset = (
            self._get_queryset()
            .annotate(
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
                            + F(f"technology_vulnerability_{severity.value.lower()}")
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
                *[f"vulnerabilities_{severity.value.lower()}" for severity in Severity],
            )
            .order_by("-vulnerabilities", "-fixed_vulnerabilities")[: self.top]
        )
        return self._serialize(
            HostVulnerabilities,
            [
                {
                    **{
                        k: v
                        for k, v in item.items()
                        if k
                        in ["id", "address", "vulnerabilities", "fixed_vulnerabilities"]
                    },
                    "vulnerabilities_per_severity": [
                        {
                            "severity": severity.value,
                            "count": item.get(
                                f"vulnerabilities_{severity.value.lower()}"
                            ),
                        }
                        for severity in Severity
                        if item.get(f"vulnerabilities_{severity.value.lower()}")
                    ],
                }
                for item in queryset
            ],
        )

    def get_os_distribution(self, instance: Any) -> OSCount(many=True):
        return self._serialize(
            OSCount,
            self._get_queryset()
            .filter(is_fixed=False)
            .values("os_type")
            .annotate(count=Count("os_type"))
            .order_by("-count"),
        )

    def get_services_distribution(self, instance: Any) -> PortCount(many=True):
        return self._serialize(
            PortCount,
            self._get_queryset(Port)
            .filter(is_fixed=False)
            .values("service", "protocol", "port")
            .annotate(count=Count("service"))
            .order_by("-count"),
        )

    def get_technologies_distribution(
        self, instance: Any
    ) -> TechnologyCount(many=True):
        return self._serialize(
            TechnologyCount,
            self._get_queryset(Technology)
            .filter(is_fixed=False)
            .values("name")
            .annotate(count=Count("name"))
            .order_by("-count"),
        )


class HostEvolutionSerializer(StatsSerializer):
    hosts = SerializerMethodField(read_only=True)
    ports = SerializerMethodField(read_only=True)

    def _get_date_count(self, date: date, model: type[BaseModel]) -> Any:
        return (
            self._get_queryset(model)
            .annotate(start_dt=Min("executions__start"))
            .annotate(start=TruncDate("start_dt"))
            .annotate(fixed=TruncDate("fixed_date"))
            .filter(start__lte=date)
            .filter(Q(is_fixed=False) | Q(fixed__gt=date))
            .count()
        )

    def get_hosts(self, instance: Any) -> DateCount(many=True):
        return self._get_serialized_evolution(DateCount, Host)

    def get_ports(self, instance: Any) -> DateCount(many=True):
        return self._get_serialized_evolution(DateCount, Port)


class VulnerabilityStatsSerializer(StatsSerializer):
    fix_progress = SerializerMethodField(read_only=True)
    fix_progress_per_severity = SerializerMethodField(read_only=True)
    trending_cve = SerializerMethodField(read_only=True)
    fixed_trending_cve = SerializerMethodField(read_only=True)
    top_cve = SerializerMethodField(read_only=True)
    top_fixed_cve = SerializerMethodField(read_only=True)
    cwe_distribution = SerializerMethodField(read_only=True)
    fixed_cwe_distribution = SerializerMethodField(read_only=True)
    severity_distribution = SerializerMethodField(read_only=True)
    fixed_severity_distribution = SerializerMethodField(read_only=True)
    model = Vulnerability

    _current_vulnerabilities = None
    _fixed_vulnerabilities = None

    def _get_vulnerabilities(self, fixed: bool) -> QuerySet:
        if not self._current_vulnerabilities:
            self._current_vulnerabilities = (
                self._get_queryset()
                .filter(is_fixed=False)
                .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            )
        if not self._fixed_vulnerabilities:
            self._fixed_vulnerabilities = (
                self._get_queryset()
                .filter(is_fixed=True)
                .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            )
        return self._fixed_vulnerabilities if fixed else self._current_vulnerabilities

    def get_fix_progress(self, instance: Any) -> float:
        all = (
            self._get_queryset()
            .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            .exclude(triage_status=TriageStatus.WONT_FIX)
            .count()
        )
        return (
            round(
                (
                    self._get_vulnerabilities(True)
                    .exclude(triage_status=TriageStatus.WONT_FIX)
                    .count()
                    / all
                )
                * 100,
                2,
            )
            if all
            else 0.0
        )

    def get_fix_progress_per_severity(
        self, instance: Any
    ) -> SeverityProgress(many=True):
        return self._serialize(
            SeverityProgress,
            self._get_queryset()
            .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
            .exclude(triage_status=TriageStatus.WONT_FIX)
            .values("severity")
            .annotate(count=Count("id", distinct=True))
            .annotate(count_fixed=Count("id", distinct=True, filter=Q(is_fixed=True)))
            .annotate(
                progress=ExpressionWrapper(
                    (F("count_fixed") * 1.0 / F("count")) * 100,
                    output_field=Float(),
                )
            )
            .order_by("-severity"),
        )

    def _get_trending_cve(self, fixed: bool) -> CveCount(many=True):
        return self._serialize(
            CveCount,
            self._get_vulnerabilities(fixed)
            .exclude(cve=None)
            .annotate(link=Max("reference"))
            .annotate(severity_value=Max("severity"))
            .values("cve", "severity_value", "link")
            .annotate(count=Count("cve"))
            .order_by("-count"),
        )

    def get_trending_cve(self, instance: Any) -> CveCount(many=True):
        return self._get_trending_cve(False)

    def get_fixed_trending_cve(self, instance: Any) -> CveCount(many=True):
        return self._get_trending_cve(True)

    def _get_top_cve(self, fixed: bool) -> CveCount(many=True):
        return self._serialize(
            CveCount,
            self._get_vulnerabilities(fixed)
            .exclude(cve=None)
            .annotate(link=Max("reference"))
            .values("cve", "link")
            .annotate(severity_value=Max("severity"))
            .values("cve", "severity_value", "link")
            .annotate(count=Count("cve"))
            .order_by("-count")[: self.top],
        )

    def get_top_cve(self, instance: Any) -> CveCount(many=True):
        return self._get_top_cve(False)

    def get_top_fixed_cve(self, instance: Any) -> CveCount(many=True):
        return self._get_top_cve(True)

    def _get_cwe_distribution(self, fixed: bool) -> CweCount(many=True):
        return self._serialize(
            CweCount,
            self._get_vulnerabilities(fixed)
            .exclude(cwe=None)
            .values("cwe")
            .annotate(count=Count("cwe"))
            .order_by("-count")[: self.top],
        )

    def get_cwe_distribution(self, instance: Any) -> CweCount(many=True):
        return self._get_cwe_distribution(False)

    def get_fixed_cwe_distribution(self, instance: Any) -> CweCount(many=True):
        return self._get_cwe_distribution(True)

    def _get_severity_distribution(self, fixed: bool) -> SeverityCount(many=True):
        return self._serialize(
            SeverityCount,
            self._get_vulnerabilities(fixed)
            .values("severity")
            .annotate(count=Count("severity"))
            .order_by("-count"),
        )

    def get_severity_distribution(self, instance: Any) -> SeverityCount(many=True):
        return self._get_severity_distribution(False)

    def get_fixed_severity_distribution(
        self, instance: Any
    ) -> SeverityCount(many=True):
        return self._get_severity_distribution(True)


class VulnerabilityEvolutionSerializer(StatsSerializer):
    evolution = SerializerMethodField(read_only=True)
    model = Vulnerability

    def get_evolution(self, instance: Any) -> DateSeverityCount(many=True):
        return self._get_serialized_evolution(DateSeverityCount)

    def _get_evolution(self, model: BaseModel | None = None) -> list[dict[str, Any]]:
        return sum(super()._get_evolution(model), [])

    def _get_date_evolution(self, date: date, count: Any) -> Any:
        return [{"date": date, **item} for item in count]

    def _get_date_count(self, date: date, model: BaseModel) -> Any:
        return [
            {
                "severity": severity,
                "count": self._get_queryset()
                .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .annotate(start_dt=Min("executions__start"))
                .annotate(start=TruncDate("start_dt"))
                .annotate(fixed=TruncDate("fixed_date"))
                .filter(start__lte=date, severity=severity)
                .filter(Q(is_fixed=False) | Q(fixed__gt=date))
                .count(),
            }
            for severity in Severity
        ]


class TriagingStatsSerializer(StatsSerializer):
    fp_rate = SerializerMethodField(read_only=True)
    distribution = SerializerMethodField(read_only=True)

    def get_fp_rate(self, instance: Any) -> float:
        all = 0
        fps = 0
        for model in [OSINT, Credential, Vulnerability, Exploit]:
            all += self._get_queryset(model).count()
            fps += (
                self._get_queryset(model)
                .filter(triage_status=TriageStatus.FALSE_POSITIVE)
                .count()
            )
        return round((fps / all) * 100, 2) if all > 0 else 0.0

    def get_distribution(self, instance: Any) -> TriageStatusCount(many=True):
        distribution: dict[str, int] = {}
        for model in [OSINT, Credential, Vulnerability, Exploit]:
            distribution.update(
                {
                    i["triage_status"]: distribution.get(i["triage_status"], 0)
                    + i.get("count", 0)
                    for i in self._get_queryset(model)
                    .filter(is_fixed=False)
                    .values("triage_status")
                    .annotate(count=Count("id", distinct=True))
                    .order_by("-count")
                }
            )
        return self._serialize(
            TriageStatusCount,
            [{"status": k, "count": v} for k, v in distribution.items()],
        )

from datetime import datetime, timedelta
from typing import Any

from django.db.models import Count, ExpressionWrapper, F
from django.db.models import FloatField as Float
from django.db.models import Max, Q, QuerySet
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
from projects.models import Project
from projects.serializers import ProjectSerializer
from rest_framework.serializers import (
    CharField,
    FloatField,
    IntegerField,
    PrimaryKeyRelatedField,
    Serializer,
    SerializerMethodField,
)
from targets.models import Target
from tasks.models import Task
from tasks.serializers import TaskSerializer


class QueueStatsSerializer(Serializer):
    jobs = IntegerField()
    workers = IntegerField()
    finished_jobs = IntegerField()
    started_jobs = IntegerField()
    deferred_jobs = IntegerField()
    failed_jobs = IntegerField()
    scheduled_jobs = IntegerField()


class RQStatsSerializer(Serializer):
    tasks = QueueStatsSerializer()
    executions = QueueStatsSerializer()
    findings = QueueStatsSerializer()
    monitor = QueueStatsSerializer()


class StatsSerializer(Serializer):
    top = 5

    def _filter(self, queryset: QuerySet, time_field: str | None = None) -> QuerySet:
        project_field = queryset.model.get_project_field()
        filters = {
            (
                f"{project_field}__members__id" if project_field else "members__id"
            ): self.context.get("request").user.id
        }
        if self.validated_data.get("target"):
            filters[project_field.split("__project")[0]] = self.validated_data.get(
                "target"
            )
        elif self.validated_data.get("project"):
            filters[project_field] = self.validated_data.get("project")
        if self.validated_data.get("months") and time_field:
            filters[f"{time_field}__gte"] = datetime.now() - timedelta(
                days=self.validated_data.get("months", 0) * 30
            )
        return queryset.filter(**filters)


class ScopeSerializer(StatsSerializer):
    project = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, queryset=Project.objects.all()
    )
    target = PrimaryKeyRelatedField(
        many=False, write_only=True, required=False, queryset=Target.objects.all()
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs.get("target"):
            attrs["project"] = None
        return super().validate(attrs)


class TimelineSerializer(StatsSerializer):
    months = IntegerField(max_value=24, min_value=1, required=False, write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("months"):
            attrs["months"] = 6
        return super().validate(attrs)


class ScopeTimelineSerializer(ScopeSerializer, TimelineSerializer):
    pass


# TODO: Improve performance or UX during loading
class ActivityStatsSerializer(ScopeSerializer):
    latest_tasks = SerializerMethodField(read_only=True)
    latest_hosts = SerializerMethodField(read_only=True)
    latest_vulnerabilities = SerializerMethodField(read_only=True)
    top_projects = SerializerMethodField(read_only=True)

    def get_latest_tasks(self, instance: Any) -> TaskSerializer(many=True):
        return TaskSerializer(
            self._filter(Task.objects.exclude(start=None).order_by("-start"))[
                : self.top
            ],
            many=True,
        ).data

    def get_latest_hosts(self, instance: Any) -> HostSerializer(many=True):
        return HostSerializer(
            self._filter(
                Host.objects.filter(is_fixed=False)
                .annotate(max_start=Max("executions__start"))
                .order_by("-max_start")
            )[: self.top],
            many=True,
        ).data

    def get_latest_vulnerabilities(
        self, instance: Any
    ) -> VulnerabilitySerializer(many=True):
        return VulnerabilitySerializer(
            self._filter(
                Vulnerability.objects.filter(is_fixed=False)
                .exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .annotate(max_start=Max("executions__start"))
                .order_by("-max_start"),
            )[: self.top],
            many=True,
        ).data

    def get_top_projects(self, instance: Any) -> ProjectSerializer(many=True):
        return ProjectSerializer(
            (
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
            many=True,
        ).data


class HostVulnerabilitiesSerializer(Serializer):
    id = IntegerField()
    address = CharField()
    vulnerabilities = IntegerField()
    vulnerabilities_critical = IntegerField()
    vulnerabilities_high = IntegerField()
    vulnerabilities_medium = IntegerField()
    vulnerabilities_low = IntegerField()
    vulnerabilities_info = IntegerField()
    fixed_vulnerabilities = IntegerField()


class OSCountSerializer(Serializer):
    os_type = CharField()
    count = IntegerField()


class PortCountSerializer(Serializer):
    port = IntegerField()
    protocol = CharField()
    service = CharField()
    count = IntegerField()


class TechnologyCountSerializer(Serializer):
    name = CharField()
    count = IntegerField()


class HostsStatsSerializer(ScopeSerializer):
    top_vulnerable = SerializerMethodField(read_only=True)
    os_distribution = SerializerMethodField(read_only=True)
    services_distribution = SerializerMethodField(read_only=True)
    technologies_distribution = SerializerMethodField(read_only=True)

    def get_top_vulnerable(
        self, instance: Any
    ) -> HostVulnerabilitiesSerializer(many=True):
        return HostVulnerabilitiesSerializer(
            self._filter(
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
                .order_by("-vulnerabilities", "-fixed_vulnerabilities")
            )[: self.top],
            many=True,
        ).data

    def get_os_distribution(self, instance: Any) -> OSCountSerializer(many=True):
        return OSCountSerializer(
            self._filter(
                Host.objects.filter(is_fixed=False)
                .values("os_type")
                .annotate(count=Count("os_type"))
                .order_by("-count"),
            ),
            many=True,
        ).data

    def get_services_distribution(
        self, instance: Any
    ) -> PortCountSerializer(many=True):
        return PortCountSerializer(
            self._filter(
                Port.objects.filter(is_fixed=False)
                .values("service", "protocol", "port")
                .annotate(count=Count("service"))
                .order_by("-count"),
            ),
            many=True,
        ).data

    def get_technologies_distribution(
        self, instance: Any
    ) -> TechnologyCountSerializer(many=True):
        return TechnologyCountSerializer(
            self._filter(
                Technology.objects.filter(is_fixed=False)
                .values("name")
                .annotate(count=Count("name"))
                .order_by("-count")
            ),
            many=True,
        ).data


class CveCountSerializer(Serializer):
    cve = CharField()
    max_severity = CharField()
    link = CharField()
    count = IntegerField()


class CweCountSerializer(Serializer):
    cwe = CharField()
    count = IntegerField()


class SeverityCountSerializer(Serializer):
    severity = CharField()
    count = IntegerField()


class SeverityProgressSerializer(Serializer):
    severity = CharField()
    progress = FloatField()


class VulnerabilityStatsSerializer(ScopeSerializer):
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

    _current_vulnerabilities = Vulnerability.objects.filter(is_fixed=False).exclude(
        triage_status=TriageStatus.FALSE_POSITIVE
    )
    _fixed_vulnerabilities = Vulnerability.objects.filter(is_fixed=True).exclude(
        triage_status=TriageStatus.FALSE_POSITIVE
    )

    def _get_queryset(self, fixed: bool) -> QuerySet:
        return self._fixed_vulnerabilities if fixed else self._current_vulnerabilities

    def get_fix_progress(self, instance: Any) -> float:
        all = self._filter(
            Vulnerability.objects.exclude(
                triage_status=TriageStatus.FALSE_POSITIVE
            ).exclude(triage_status=TriageStatus.WONT_FIX)
        ).count()
        return (
            round(
                (
                    self._filter(
                        self._fixed_vulnerabilities.exclude(
                            triage_status=TriageStatus.WONT_FIX
                        )
                    ).count()
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
    ) -> SeverityProgressSerializer(many=True):
        return SeverityProgressSerializer(
            self._filter(
                Vulnerability.objects.exclude(triage_status=TriageStatus.FALSE_POSITIVE)
                .exclude(triage_status=TriageStatus.WONT_FIX)
                .values("severity")
                .annotate(count=Count("id", distinct=True))
                .annotate(
                    count_fixed=Count("id", distinct=True, filter=Q(is_fixed=True))
                )
                .annotate(
                    progress=ExpressionWrapper(
                        (F("count_fixed") * 1.0 / F("count")) * 100,
                        output_field=Float(),
                    )
                )
                .order_by("-severity")
            ),
            many=True,
        ).data

    def _get_trending_cve(self, fixed: bool) -> CveCountSerializer(many=True):
        return CveCountSerializer(
            self._filter(
                self._get_queryset(fixed)
                .filter(trending=True)
                .annotate(link=Max("reference"))
                .annotate(max_severity=Max("severity"))
                .values("cve", "max_severity", "link")
                .annotate(count=Count("cve"))
                .order_by("-count")
            ),
            many=True,
        ).data

    def get_trending_cve(self, instance: Any) -> CveCountSerializer(many=True):
        return self._get_trending_cve(False)

    def get_fixed_trending_cve(self, instance: Any) -> CveCountSerializer(many=True):
        return self._get_trending_cve(True)

    def _get_top_cve(self, fixed: bool) -> CveCountSerializer(many=True):
        return CveCountSerializer(
            self._filter(
                self._get_queryset(fixed)
                .exclude(cve=None)
                .annotate(link=Max("reference"))
                .values("cve", "link")
                .annotate(max_severity=Max("severity"))
                .values("cve", "max_severity", "link")
                .annotate(count=Count("cve"))
                .order_by("-count")
            )[: self.top],
            many=True,
        ).data

    def get_top_cve(self, instance: Any) -> CveCountSerializer(many=True):
        return self._get_top_cve(False)

    def get_top_fixed_cve(self, instance: Any) -> CveCountSerializer(many=True):
        return self._get_top_cve(True)

    def _get_cwe_distribution(self, fixed: bool) -> CweCountSerializer(many=True):
        return CweCountSerializer(
            self._filter(
                self._get_queryset(fixed)
                .exclude(cwe=None)
                .values("cwe")
                .annotate(count=Count("cwe"))
                .order_by("-count")
            )[: self.top],
            many=True,
        ).data

    def get_cwe_distribution(self, instance: Any) -> CweCountSerializer(many=True):
        return self._get_cwe_distribution(False)

    def get_fixed_cwe_distribution(
        self, instance: Any
    ) -> CweCountSerializer(many=True):
        return self._get_cwe_distribution(True)

    def _get_severity_distribution(
        self, fixed: bool
    ) -> SeverityCountSerializer(many=True):
        return SeverityCountSerializer(
            self._filter(
                self._get_queryset(fixed)
                .values("severity")
                .annotate(count=Count("severity"))
                .order_by("-count")
            ),
            many=True,
        ).data

    def get_severity_distribution(
        self, instance: Any
    ) -> SeverityCountSerializer(many=True):
        return self._get_severity_distribution(False)

    def get_fixed_severity_distribution(
        self, instance: Any
    ) -> SeverityCountSerializer(many=True):
        return self._get_severity_distribution(True)


class TriageStatusCountSerializer(Serializer):
    status = CharField()
    count = IntegerField()


class TriagingStatsSerializer(ScopeSerializer):
    fp_rate = SerializerMethodField(read_only=True)
    distribution = SerializerMethodField(read_only=True)

    def get_fp_rate(self, instance: Any) -> float:
        all = 0
        fps = 0
        for model in [OSINT, Credential, Vulnerability, Exploit]:
            all += self._filter(model.objects.all()).count()
            fps += self._filter(
                model.objects.filter(triage_status=TriageStatus.FALSE_POSITIVE)
            ).count()
        return round((fps / all) * 100, 2) if all > 0 else 0.0

    def get_distribution(self, instance: Any) -> TriageStatusCountSerializer(many=True):
        distribution: dict[str, int] = {}
        for model in [OSINT, Credential, Vulnerability, Exploit]:
            distribution.update(
                {
                    i["triage_status"]: distribution.get(i["triage_status"], 0)
                    + i.get("count", 0)
                    for i in self._filter(
                        model.objects.filter(is_fixed=False)
                        .values("triage_status")
                        .annotate(count=Count("triage_status"))
                        .order_by("-count")
                    )
                }
            )
        return TriageStatusCountSerializer(
            [{"status": k, "count": v} for k, v in distribution.items()], many=True
        ).data

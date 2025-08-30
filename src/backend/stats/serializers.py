from backend.targets.models import Target
from django.forms import DateField
from rest_framework.serializers import CharField, FloatField, IntegerField, Serializer

from findings.enums import Severity
from findings.models import Host, Port, Technology, Vulnerability
from framework.fields import IntegerChoicesField


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


class VulnerabilityCountPerSeveritySerializer(Serializer):
    critical = IntegerField()
    high = IntegerField()
    medium = IntegerField()
    low = IntegerField()
    info = IntegerField()


class VulnerabilityCountPerStatusSerializer(Serializer):
    fixed = IntegerField()
    open = IntegerField()


class HostStatsSerializer(Serializer):
    os_type = CharField()
    count = IntegerField()

    class Meta:
        model = Host


class HostVulnerabilitiesStatsSerializer(Serializer):
    id = IntegerField()
    ip = CharField()
    domain = CharField()
    # TODO: Adapt format in the frontend
    vulnerabilities = VulnerabilityCountPerStatusSerializer()
    vulnerabilities_per_severity = VulnerabilityCountPerSeveritySerializer()

    class Meta:
        model = Host


class PortStatsSerializer(Serializer):
    port = IntegerField()
    protocol = CharField()
    service = CharField()
    count = IntegerField()

    class Meta:
        model = Port


class TechnologyStatsSerializer(Serializer):
    name = CharField()
    count = IntegerField()

    class Meta:
        model = Technology


class VulnerabilityCVEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    cve = CharField()
    severity_value = IntegerChoicesField(model=Severity)
    link = CharField()

    class Meta:
        model = Vulnerability


class VulnerabilityCWEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    cwe = CharField()

    class Meta:
        model = Vulnerability


class VulnerabilitySeverityStatsSerializer(VulnerabilityCountPerStatusSerializer):
    severity = IntegerChoicesField(model=Severity)

    class Meta:
        model = Vulnerability


class VulnerabilityFixProgressStatsSerializer(VulnerabilityCountPerStatusSerializer):
    progress = FloatField()

    class Meta:
        model = Vulnerability


class VulnerabilityFixProgressPerSeverityStatsSerializer(
    VulnerabilityFixProgressStatsSerializer, VulnerabilitySeverityStatsSerializer
):
    class Meta:
        model = Vulnerability


class TriagingStatsSerializer(VulnerabilityCountPerStatusSerializer):
    triage_status = CharField()

    class Meta:
        # TODO: Review if authorization and filters work. The QuerySet will include data from different models
        model = Vulnerability


class EvolutionStatsSerializer(Serializer):
    date = DateField()
    count = IntegerField()


class EvolutionPerSeverityStatsSerializer(EvolutionStatsSerializer):
    severity = IntegerChoicesField(model=Severity)

    class Meta:
        model = Vulnerability

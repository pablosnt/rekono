from rest_framework.serializers import BooleanField, CharField, DateField, IntegerField, Serializer

from findings.enums import Severity
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


class VulnerabilityCountPerStatusSerializer(Serializer):
    fixed = IntegerField()
    open = IntegerField()


class CountSerializer(Serializer):
    count = IntegerField()


# Similar to the previous one, but we need it to group by is_fixed
class VulnerabilityCountPerIsFixedSerializer(CountSerializer):
    is_fixed = BooleanField()


class HostStatsSerializer(CountSerializer):
    os_type = CharField()


class HostVulnerabilitiesStatsSerializer(VulnerabilityCountPerStatusSerializer):
    id = IntegerField()
    ip = CharField()
    domain = CharField()
    critical = IntegerField()
    high = IntegerField()
    medium = IntegerField()
    low = IntegerField()
    info = IntegerField()


class PortStatsSerializer(CountSerializer):
    port = IntegerField()
    protocol = CharField()
    service = CharField()


class TechnologyStatsSerializer(CountSerializer):
    name = CharField()


class VulnerabilityCVEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    cve = CharField()
    severity_value = IntegerChoicesField(model=Severity)
    link = CharField()


class VulnerabilityCWEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    cwe = CharField()


class VulnerabilitySeverityStatsSerializer(VulnerabilityCountPerStatusSerializer):
    severity = IntegerChoicesField(model=Severity)


class TriagingStatsSerializer(VulnerabilityCountPerStatusSerializer):
    triage_status = CharField()


class EvolutionStatsSerializer(CountSerializer):
    date = DateField()


class EvolutionPerSeverityStatsSerializer(EvolutionStatsSerializer):
    severity = IntegerChoicesField(model=Severity)

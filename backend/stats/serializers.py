"""Serializers of the statistics endpoints.

The statistics aren't models, they are the result of aggregating the findings, so
these serializers only give the calculated data a stable shape.
"""

from rest_framework.serializers import BooleanField, CharField, DateField, IntegerField, Serializer

from findings.enums import Severity
from framework.fields import IntegerChoicesField


class QueueStatsSerializer(Serializer):
    """Serializer of the state of one RQ queue.

    Attributes:
        jobs: Jobs waiting to be run.
        workers: Workers attending the queue.
        finished_jobs: Jobs that completed successfully.
        started_jobs: Jobs that are being run right now.
        deferred_jobs: Jobs waiting for the ones that they depend on.
        failed_jobs: Jobs that raised an exception.
        scheduled_jobs: Jobs that will be run at a given time.
    """

    jobs = IntegerField()
    workers = IntegerField()
    finished_jobs = IntegerField()
    started_jobs = IntegerField()
    deferred_jobs = IntegerField()
    failed_jobs = IntegerField()
    scheduled_jobs = IntegerField()


class RQStatsSerializer(Serializer):
    """Serializer of the state of all the RQ queues.

    Attributes:
        tasks: Queue that splits the tasks into executions.
        executions: Queue that runs the tools.
        findings: Queue that processes the findings that the tools report.
        monitor: Queue that refreshes the vulnerability data.
    """

    tasks = QueueStatsSerializer()
    executions = QueueStatsSerializer()
    findings = QueueStatsSerializer()
    monitor = QueueStatsSerializer()


class VulnerabilityCountPerStatusSerializer(Serializer):
    """Serializer of how many findings are fixed and how many aren't.

    Attributes:
        fixed: Findings that aren't there anymore.
        open: Findings that are still there.
    """

    fixed = IntegerField()
    open = IntegerField()


class CountSerializer(Serializer):
    """Serializer of how many findings share something.

    Attributes:
        count: Findings counted in the group.
    """

    count = IntegerField()


class HostStatsSerializer(CountSerializer):
    """Serializer of how many hosts run each operating system.

    Attributes:
        os_type: Operating system family of the hosts.
    """

    os_type = CharField()


class HostVulnerabilitiesStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer of the vulnerabilities found in each host.

    Attributes:
        id: Identifier of the host.
        ip: IP address of the host.
        domain: Domain name of the host.
        critical: Open vulnerabilities with critical severity.
        high: Open vulnerabilities with high severity.
        medium: Open vulnerabilities with medium severity.
        low: Open vulnerabilities with low severity.
        info: Open vulnerabilities with informative severity.
    """

    id = IntegerField()
    ip = CharField()
    domain = CharField()
    critical = IntegerField()
    high = IntegerField()
    medium = IntegerField()
    low = IntegerField()
    info = IntegerField()


class PortStatsSerializer(CountSerializer):
    """Serializer of how many hosts expose each service.

    Attributes:
        port: Port number where the service was found.
        protocol: Transport protocol of the port.
        service: Service that listens on the port.
    """

    port = IntegerField()
    protocol = CharField()
    service = CharField()


class TechnologyStatsSerializer(CountSerializer):
    """Serializer of how many times each technology was found.

    Attributes:
        name: Name of the technology.
    """

    name = CharField()


class VulnerabilityCVEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer of how many times each CVE was found.

    Attributes:
        cve: CVE identifier of the vulnerability.
        severity_value: Severity of the vulnerability, as its name.
        link: Link to the advisory of the vulnerability.
    """

    cve = CharField()
    severity_value = IntegerChoicesField(model=Severity)
    link = CharField()


class VulnerabilityCWEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer of how many vulnerabilities belong to each weakness.

    Attributes:
        cwe: CWE identifier of the weakness.
    """

    cwe = CharField()


class VulnerabilitySeverityStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer of how many vulnerabilities have each severity.

    Attributes:
        severity: Severity of the vulnerabilities, as its name.
    """

    severity = IntegerChoicesField(model=Severity)


class TriagingStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer of how many findings are in each triage status.

    Attributes:
        triage_status: Decision that the auditors took about the findings.
    """

    triage_status = CharField()


class ExploitCoverageStatsSerializer(CountSerializer):
    """Serializer of how many vulnerabilities have a public exploit.

    Attributes:
        has_exploits: Whether the counted vulnerabilities have exploits or not.
    """

    has_exploits = BooleanField()


class FindingsEvolutionStatsSerializer(Serializer):
    """Serializer of how the findings of one type evolved during a month.

    Attributes:
        month: First day of the month that the data belongs to.
        discovered: Findings discovered for the first time during the month.
        fixed: Findings fixed during the month.
        active: Findings that were still there when the month ended.
    """

    month = DateField()
    discovered = IntegerField()
    fixed = IntegerField()
    active = IntegerField()

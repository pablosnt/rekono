"""Django REST framework serializers for statistics data conversion.

Provides serializer classes for statistics API responses including queue monitoring,
vulnerability analytics, host statistics, and evolution data with field validation
and type conversion for consistent API data formats.
"""

from rest_framework.serializers import BooleanField, CharField, DateField, IntegerField, Serializer

from findings.enums import Severity
from framework.fields import IntegerChoicesField


class QueueStatsSerializer(Serializer):
    """Serializer for background job queue statistics.

    Handles serialization of Redis Queue (RQ) statistics including job counts,
    worker status, and queue health metrics for system monitoring.

    Attributes:
        jobs (IntegerField): Total number of jobs in the queue
        workers (IntegerField): Number of active worker processes
        finished_jobs (IntegerField): Count of completed jobs
        started_jobs (IntegerField): Count of currently running jobs
        deferred_jobs (IntegerField): Count of deferred/scheduled jobs
        failed_jobs (IntegerField): Count of failed job executions
        scheduled_jobs (IntegerField): Count of scheduled future jobs
    """

    jobs = IntegerField()
    workers = IntegerField()
    finished_jobs = IntegerField()
    started_jobs = IntegerField()
    deferred_jobs = IntegerField()
    failed_jobs = IntegerField()
    scheduled_jobs = IntegerField()


class RQStatsSerializer(Serializer):
    """Serializer for comprehensive Redis Queue statistics across all queue types.

    Aggregates queue statistics for different job categories including tasks,
    executions, findings processing, and monitoring operations.

    Attributes:
        tasks (QueueStatsSerializer): Statistics for task execution queue
        executions (QueueStatsSerializer): Statistics for tool execution queue
        findings (QueueStatsSerializer): Statistics for findings processing queue
        monitor (QueueStatsSerializer): Statistics for monitoring operations queue
    """

    tasks = QueueStatsSerializer()
    executions = QueueStatsSerializer()
    findings = QueueStatsSerializer()
    monitor = QueueStatsSerializer()


class VulnerabilityCountPerStatusSerializer(Serializer):
    """Serializer for vulnerability counts categorized by fix status.

    Provides counts of vulnerabilities segmented by their remediation status
    for tracking security posture improvements.

    Attributes:
        fixed (IntegerField): Number of remediated vulnerabilities
        open (IntegerField): Number of unresolved vulnerabilities
    """

    fixed = IntegerField()
    open = IntegerField()


class CountSerializer(Serializer):
    """Base serializer for basic count statistics.

    Provides a simple count field for statistical data aggregation
    across various finding types and categories.

    Attributes:
        count (IntegerField): Numeric count value
    """

    count = IntegerField()


# Similar to the previous one, but we need it to group by is_fixed
class VulnerabilityCountPerIsFixedSerializer(CountSerializer):
    """Serializer for vulnerability counts grouped by remediation status flag.

    Extends CountSerializer to include the is_fixed boolean field for
    categorizing vulnerabilities by their remediation state.

    Attributes:
        count (IntegerField): Number of vulnerabilities in this category
        is_fixed (BooleanField): Whether vulnerabilities in this group are fixed
    """

    is_fixed = BooleanField()


class HostStatsSerializer(CountSerializer):
    """Serializer for host statistics grouped by operating system type.

    Provides counts of discovered hosts categorized by their operating
    system family for infrastructure analysis.

    Attributes:
        count (IntegerField): Number of hosts in this OS category
        os_type (CharField): Operating system family identifier
    """

    os_type = CharField()


class HostVulnerabilitiesStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer for detailed host vulnerability statistics.

    Provides comprehensive vulnerability counts per host including severity
    breakdown and status tracking for targeted remediation efforts.

    Attributes:
        id (IntegerField): Host record identifier
        ip (CharField): Host IP address
        domain (CharField): Associated domain name
        fixed (IntegerField): Number of fixed vulnerabilities
        open (IntegerField): Number of open vulnerabilities
        critical (IntegerField): Count of open critical vulnerabilities
        high (IntegerField): Count of open high vulnerabilities
        medium (IntegerField): Count of open medium vulnerabilities
        low (IntegerField): Count of open low vulnerabilities
        info (IntegerField): Count of open informational findings
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
    """Serializer for network port statistics.

    Provides aggregated statistics for discovered network services including
    port numbers, protocols, and service identification for attack surface analysis.

    Attributes:
        count (IntegerField): Number of occurrences of this service
        port (IntegerField): Port number
        protocol (CharField): Network protocol (TCP/UDP)
        service (CharField): Identified service name
    """

    port = IntegerField()
    protocol = CharField()
    service = CharField()


class TechnologyStatsSerializer(CountSerializer):
    """Serializer for technology fingerprinting statistics.

    Provides counts of identified technologies and software components
    across discovered assets for technology stack analysis.

    Attributes:
        count (IntegerField): Number of instances of this technology
        name (CharField): Technology or software component name
    """

    name = CharField()


class VulnerabilityCVEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer for CVE-based vulnerability statistics.

    Provides vulnerability counts grouped by CVE identifiers including
    severity levels and reference links for vulnerability management.

    Attributes:
        fixed (IntegerField): Number of fixed vulnerabilities for this CVE
        open (IntegerField): Number of open vulnerabilities for this CVE
        cve (CharField): CVE identifier
        severity_value (IntegerChoicesField): Severity level enumeration value
        link (CharField): Reference URL for vulnerability details
    """

    cve = CharField()
    severity_value = IntegerChoicesField(model=Severity)
    link = CharField()


class VulnerabilityCWEStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer for CWE-based vulnerability statistics.

    Provides vulnerability counts categorized by Common Weakness Enumeration
    identifiers for vulnerability pattern analysis.

    Attributes:
        fixed (IntegerField): Number of fixed vulnerabilities for this CWE
        open (IntegerField): Number of open vulnerabilities for this CWE
        cwe (CharField): CWE identifier
    """

    cwe = CharField()


class VulnerabilitySeverityStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer for vulnerability statistics grouped by severity level.

    Provides vulnerability counts categorized by severity rating (critical,
    high, medium, low, info) for security prioritization and risk assessment.

    Attributes:
        fixed (IntegerField): Number of fixed vulnerabilities for this severity
        open (IntegerField): Number of open vulnerabilities for this severity
        severity (IntegerChoicesField): Severity level enumeration value
    """

    severity = IntegerChoicesField(model=Severity)


class TriagingStatsSerializer(VulnerabilityCountPerStatusSerializer):
    """Serializer for finding statistics grouped by triage status.

    Provides counts of security findings categorized by their triage
    status for tracking security assessment progress.

    Attributes:
        fixed (IntegerField): Number of fixed findings for this triage status
        open (IntegerField): Number of open findings for this triage status
        triage_status (CharField): Triage status identifier
    """

    triage_status = CharField()


class EvolutionStatsSerializer(CountSerializer):
    """Serializer for time-series evolution statistics.

    Provides counts of items over time periods for trend analysis
    and temporal security posture tracking.

    Attributes:
        count (IntegerField): Number of items for this date period
        date (DateField): Date of the data point
    """

    date = DateField()


class EvolutionPerSeverityStatsSerializer(EvolutionStatsSerializer):
    """Serializer for time-series statistics broken down by severity level.

    Extends EvolutionStatsSerializer to include severity categorization
    for tracking security trends by risk level over time.

    Attributes:
        count (IntegerField): Number of items for this date and severity
        date (DateField): Date of the data point
        severity (IntegerChoicesField): Severity level enumeration value
    """

    severity = IntegerChoicesField(model=Severity)

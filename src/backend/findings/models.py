"""Models for security findings discovered during assessments.

Defines data models representing security findings including hosts, vulnerabilities,
credentials, and exploits. Models follow hierarchical relationships enabling
comprehensive security analysis, triage workflows, and automated reporting.
"""

from typing import Any

from django.db import models

from findings.enums import (
    HostOS,
    OSINTDataType,
    PathType,
    PortStatus,
    Protocol,
    Severity,
)
from findings.framework.models import Finding, TriageFinding
from framework.enums import InputKeyword
from target_ports.models import TargetPort
from targets.enums import TargetType
from targets.models import Target


class OSINT(TriageFinding):
    """Model representing Open Source Intelligence findings from reconnaissance.

    Represents data discovered through passive reconnaissance and Open Source Intelligence
    (OSINT) techniques. These findings serve as the foundation for target enumeration
    and serve as input for further active reconnaissance phases. The model supports
    various data types including network identifiers, credentials, and organizational
    information discovered from public sources.

    Attributes:
        data (TextField): The discovered OSINT data content (max 250 characters)
        data_type (TextField): Classification from OSINTDataType enum (max 10 characters)
        source (TextField): Discovery source or platform identifier (optional, max 50 characters)

    Example:
        Create an OSINT finding for a discovered domain:

        ```python
        osint = OSINT.objects.create(
            data="example.com",
            data_type=OSINTDataType.DOMAIN,
            source="DNS enumeration"
        )
        ```
    """

    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=OSINTDataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)

    unique_fields = ["data", "data_type"]
    _parse_mapping = {
        InputKeyword.TARGET: "data",
        InputKeyword.HOST: "data",
        InputKeyword.URL: lambda instance: instance.get_url(instance.data),
    }
    _defectdojo_finding_mapping = {
        "title": lambda instance: f"{instance.data_type} found using OSINT techniques",
        "description": lambda instance: "\n".join(
            [f"{k}: {v}" for k, v in [("Data", instance.data), ("Source", instance.source)] if v]
        ),
        "severity": Severity.MEDIUM,
    }

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Parse OSINT data for tool execution input.

        Processes IP and Domain OSINT data types for use as tool execution
        targets, filtering out non-targetable data types.

        Args:
            accumulated (dict[str, Any]): Previously accumulated parsing data.

        Returns:
            dict[str, Any]: Parsed data for target creation, empty for non-targetable types.
        """
        return super().parse(accumulated) if self.data_type in [OSINTDataType.IP, OSINTDataType.DOMAIN] else {}


class Host(Finding):
    """Model representing network hosts discovered during reconnaissance and scanning.

    Represents network hosts identified during active and passive reconnaissance phases.
    Each host record contains network identifiers, system information, and geolocation
    data essential for asset inventory and attack surface mapping. Hosts serve as the
    foundation for port scanning, service enumeration, and vulnerability assessment.

    Attributes:
        ip (TextField): IPv4 or IPv6 address identifier (max 30 characters)
        domain (TextField): Associated domain name or hostname (optional, max 500 characters)
        os (TextField): Detailed operating system identification (optional, max 250 characters)
        os_type (TextField): OS family classification from HostOS enum (default: OTHER, max 10 characters)
        country (TextField): Geolocation country name (optional, max 100 characters)
        city (TextField): Geolocation city name (optional, max 100 characters)
        latitude (FloatField): Geographic latitude coordinate (optional)
        longitude (FloatField): Geographic longitude coordinate (optional)

    Example:
        Create a host finding with geolocation data:

        ```python
        host = Host.objects.create(
            ip="192.168.1.100",
            domain="server.example.com",
            os="Ubuntu 20.04.3 LTS",
            os_type=HostOS.LINUX,
            country="United States",
            city="San Francisco"
        )
        ```
    """

    ip = models.TextField(max_length=30)
    domain = models.TextField(max_length=500, blank=True, null=True)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.TextField(max_length=10, choices=HostOS.choices, default=HostOS.OTHER)
    country = models.TextField(max_length=100, blank=True, null=True)
    city = models.TextField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    reputation = models.IntegerField(blank=True, null=True)
    harmless_votes = models.IntegerField(blank=True, null=True)
    malicious_votes = models.IntegerField(blank=True, null=True)
    whois = models.TextField(blank=True, null=True)

    unique_fields = ["ip"]
    _filters = [Finding.Filter(TargetType, "ip", processor=lambda a: Target.get_type(a))]
    _parse_mapping = {
        InputKeyword.TARGET: "ip",
        InputKeyword.HOST: "ip",
        InputKeyword.URL: lambda instance: instance.get_url(instance.ip),
    }
    _defectdojo_finding_mapping = {
        "title": "Host discovered",
        "description": lambda instance: "\n".join(
            [
                f"{k}: {v}"
                for k, v in [
                    ("IP", instance.ip),
                    ("Domain", instance.domain),
                    ("OS type", instance.os_type),
                    ("OS", instance.os),
                    ("Country", instance.country),
                    ("City", instance.city),
                    ("Latitude", instance.latitude),
                    ("Longitude", instance.longitude),
                ]
                if v
            ]
        ),
        "severity": Severity.INFO,
    }


class Port(Finding):
    """Model representing network services discovered during port scanning and enumeration.

    Represents network ports and associated services identified during active reconnaissance
    and port scanning operations. Port findings form the foundation for service enumeration,
    vulnerability scanning, and application-layer security testing. Each port record contains
    network service information, protocol details, and connection status essential for
    attack surface analysis and security assessment planning.

    Attributes:
        host (ForeignKey): Parent host where port was discovered (optional relationship)
        port (IntegerField): Network port number in range 1-65535
        status (TextField): Port scan status from PortStatus enum (default: OPEN, max 15 characters)
        protocol (TextField): Transport protocol from Protocol enum (optional, max 5 characters)
        service (TextField): Identified service name or banner information (optional, max 50 characters)

    Example:
        Create a port finding for an identified web service:

        ```python
        port = Port.objects.create(
            host=host_instance,
            port=443,
            status=PortStatus.OPEN,
            protocol=Protocol.TCP,
            service="https"
        )
        ```
    """

    host = models.ForeignKey(Host, related_name="port", on_delete=models.DO_NOTHING, blank=True, null=True)
    port = models.IntegerField()
    status = models.TextField(max_length=15, choices=PortStatus.choices, default=PortStatus.OPEN)
    protocol = models.TextField(max_length=5, choices=Protocol.choices, blank=True, null=True)
    service = models.TextField(max_length=50, blank=True, null=True)

    unique_fields = ["host", "port", "protocol"]
    _parse_mapping = {InputKeyword.PORT: "port", InputKeyword.PORTS: lambda instance: [instance.port]}
    _defectdojo_finding_mapping = {
        "title": "Port discovered",
        "description": lambda instance: "\n".join(
            [
                f"{k}: {v}"
                for k, v in [
                    ("Host", instance.host.ip if instance.host else None),
                    ("Port", instance.port),
                    ("Status", instance.status),
                    ("Protocol", instance.protocol),
                    ("Service", instance.service),
                ]
                if v
            ]
        ),
        "severity": Severity.INFO,
    }
    _filters = [
        Finding.Filter(int, "port"),
        Finding.Filter(str, "service", contains=True, processor=lambda s: s.lower()),
    ]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Parse port data for tool execution targeting.

        Generates target specifications combining host and port information
        for detailed service-specific security analysis.

        Args:
            accumulated (dict[str, Any]): Previously accumulated parsing data.

        Returns:
            dict[str, Any]: Port-specific target data including host:port combinations.
        """
        output = super().parse(accumulated)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(p) for p in output.get(InputKeyword.PORTS.name.lower()) or []]
        )
        if self.host:
            output.update(
                {
                    InputKeyword.TARGET.name.lower(): f"{self.host.ip}:{self.port}",
                    InputKeyword.HOST.name.lower(): self.host.ip,
                    InputKeyword.URL.name.lower(): self.get_url(self.host.ip, self.port),
                }
            )
        return output


class Path(Finding):
    """Model representing web paths and endpoints discovered during application reconnaissance.

    Represents discoverable web resources including API endpoints, directory paths, file
    shares, and hidden resources found during web application security testing. Path
    findings enable comprehensive attack surface mapping for web applications and provide
    entry points for authentication bypass, privilege escalation, and data exposure testing.

    Attributes:
        port (ForeignKey): Network service where path was discovered (optional relationship)
        path (TextField): URL path or endpoint location (max 500 characters)
        status (IntegerField): HTTP response status code from server (optional)
        extra_info (TextField): Additional discovery metadata or context (optional, max 100 characters)
        type (TextField): Resource classification from PathType enum (default: ENDPOINT)

    Example:
        Create a path finding for an API endpoint:

        ```python
        path = Path.objects.create(
            port=web_port,
            path="/api/v1/users",
            status=200,
            type=PathType.ENDPOINT,
            extra_info="JSON API endpoint"
        )
        ```
    """

    port = models.ForeignKey(Port, related_name="path", on_delete=models.DO_NOTHING, blank=True, null=True)
    path = models.TextField(max_length=500)
    # Status received for that path. Probably HTTP status
    status = models.IntegerField(blank=True, null=True)
    extra_info = models.TextField(max_length=100, blank=True, null=True)
    # Path type depending on the protocol where it's found
    type = models.TextField(choices=PathType.choices, default=PathType.ENDPOINT)

    unique_fields = ["port", "path"]
    _filters = [
        Finding.Filter(PathType, "type"),
        Finding.Filter(int, "status"),
        Finding.Filter(str, "path", contains=True, processor=lambda p: p.lower()),
    ]
    _parse_mapping = {
        InputKeyword.ENDPOINT: lambda instance: instance.clean_path(instance.path),
        InputKeyword.URL: lambda instance: instance.get_url(
            instance.port.host.ip, instance.port.port, instance.clean_path(instance.path)
        )
        if instance.port and instance.port.host
        else None,
    }
    _parse_dependencies = ["port"]
    _defectdojo_finding_mapping = {
        "title": "Path discovered",
        "description": lambda instance: "\n".join(
            [
                f"{k}: {v}"
                for k, v in [
                    ("Host", instance.port.host.ip if instance.port and instance.port.host else None),
                    ("Port", instance.port.port if instance.port else None),
                    ("Path", instance.path),
                    ("Type", instance.type),
                    ("Status", instance.status),
                    ("Info", instance.extra_info),
                ]
                if v
            ]
        ),
        "severity": Severity.INFO,
    }
    _defectdojo_endpoint_mapping = {
        "protocol": lambda instance, target: instance.port.service if instance.port else None,
        "host": lambda instance, target: instance.port.host.ip
        if instance.port and instance.port.host
        else target.target,
        "port": lambda instance, target: instance.port.port if instance.port else None,
        "path": "path",
    }

    def _clean_comparison_path(self, value: str) -> str:
        """Normalize path value for comparison operations.

        Args:
            value (str): Raw path string to normalize.

        Returns:
            str: Normalized path with consistent trailing slash.
        """
        if len(value) > 1:
            value = self.clean_path(value)
            if value is None:
                value = "/"
            elif value[-1] != "/":
                value += "/"
        return value

    def filter(self, input: Any, target: Target | None = None) -> bool:
        """Filter paths against target port path restrictions.

        Applies additional filtering for paths within target port scope
        when target port paths are configured.

        Args:
            input (Any): Filter criteria to match against.
            target (Target | None): Target context for scope validation.

        Returns:
            bool: True if path matches criteria and scope restrictions.
        """
        filter = super().filter(input, target)
        if self.port:
            target_port = TargetPort.objects.filter(target=target, port=self.port.port).first()
            if target_port and target_port.path:
                # If there is a target por with path, only paths within it will be considered
                filter = filter and self._clean_comparison_path(self.path).startswith(
                    self._clean_comparison_path(target_port.path)
                )
        return filter


class Technology(Finding):
    """Model representing software technologies discovered during service fingerprinting.

    Represents software technologies, frameworks, and applications identified through
    active and passive fingerprinting techniques. Technology findings provide the
    foundation for vulnerability assessment, exploit selection, and attack vector
    identification by mapping the software stack running on discovered services.

    Attributes:
        port (ForeignKey): Network service where technology was identified (optional relationship)
        name (TextField): Technology or software name identifier (max 100 characters)
        version (TextField): Software version string or build information (optional, max 100 characters)
        description (TextField): Detailed technology information and context (optional, max 200 characters)
        reference (TextField): Documentation links or vendor information (optional, max 250 characters)

    Example:
        Create a technology finding for a web server:

        ```python
        technology = Technology.objects.create(
            port=web_port,
            name="Apache HTTP Server",
            version="2.4.41",
            description="Open-source web server software",
            reference="https://httpd.apache.org/"
        )
        ```
    """

    port = models.ForeignKey(
        Port,
        related_name="technology",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    name = models.TextField(max_length=100)
    version = models.TextField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    unique_fields = ["port", "name", "version"]
    _filters = [Finding.Filter(str, "name", contains=True, processor=lambda n: n.lower())]
    _parse_mapping = {InputKeyword.TECHNOLOGY: "name", InputKeyword.VERSION: "version"}
    _parse_dependencies = ["port"]
    _defectdojo_finding_mapping = {
        "title": lambda instance: f"Technology {instance.name} detected",
        "description": lambda instance: (f"{instance.description}\n\n" if instance.description else "")
        + "\n".join([f"{k}: {v}" for k, v in [("Technology", instance.name), ("Version", instance.version)] if v]),
        "severity": Severity.LOW,
        "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
        "references": "reference",
    }


class Credential(TriageFinding):
    """Model representing authentication credentials exposed during security assessment.

    Represents discovered usernames, passwords, API keys, tokens, and other authentication
    secrets found through credential harvesting, exposure detection, and security testing.
    Credential findings represent high-risk security exposures that enable unauthorized
    access, privilege escalation, and lateral movement within target environments.

    Attributes:
        technology (ForeignKey): Source technology where credentials were exposed (optional relationship)
        email (TextField): Associated email address or account identifier (optional, max 100 characters)
        username (TextField): Account username or login identifier (optional, max 100 characters)
        secret (TextField): Password, API key, token, or authentication secret (optional, max 300 characters)
        context (TextField): Discovery method, location, or additional context (optional, max 300 characters)

    Example:
        Create a credential finding from configuration analysis:

        ```python
        credential = Credential.objects.create(
            technology=database_tech,
            username="admin",
            secret="password123",
            context="Found in config.php file"
        )
        ```
    """

    technology = models.ForeignKey(
        Technology,
        related_name="credential",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    email = models.TextField(max_length=100, blank=True, null=True)
    username = models.TextField(max_length=100, blank=True, null=True)
    # Secret (password, key, etc.) if found
    secret = models.TextField(max_length=300, blank=True, null=True)
    context = models.TextField(max_length=300, blank=True, null=True)

    unique_fields = ["technology", "email", "username", "secret"]
    _parse_mapping = {InputKeyword.EMAIL: "email", InputKeyword.USERNAME: "username", InputKeyword.SECRET: "secret"}
    _parse_dependencies = ["technology"]
    _defectdojo_finding_mapping = {
        "title": "Credentials exposure",
        "description": lambda instance: "\n".join(
            [
                f"{k}: {v}"
                for k, v in [
                    ("Technology", instance.technology.name if instance.technology else None),
                    ("Email", instance.email),
                    ("Username", instance.username),
                    ("Secret", instance.secret),
                ]
                if v
            ]
        ),
        "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
        "severity": Severity.HIGH,
    }


class Vulnerability(TriageFinding):
    """Model representing security vulnerabilities identified during assessment.

    Represents confirmed security vulnerabilities discovered through automated scanning,
    manual testing, and code analysis. Vulnerability findings include industry-standard
    classifications, severity ratings, and trending indicators to support risk-based
    prioritization and remediation planning within enterprise security programs.

    Attributes:
        technology (ForeignKey): Vulnerable technology component (optional relationship)
        port (ForeignKey): Network service where vulnerability was identified (optional relationship)
        name (TextField): Vulnerability name or identifier (max 50 characters)
        description (TextField): Detailed technical vulnerability description (optional)
        severity (IntegerField): Risk severity level from Severity enum (default: MEDIUM)
        cve (TextField): Common Vulnerabilities and Exposures identifier (optional, max 20 characters)
        cwe (TextField): Common Weakness Enumeration classification (optional, max 20 characters)
        reference (TextField): Security advisory or documentation links (optional, max 250 characters)
        trending (BooleanField): Active exploitation or trending status indicator (default: False)

    Example:
        Create a vulnerability finding with CVE mapping:

        ```python
        vulnerability = Vulnerability.objects.create(
            technology=web_server,
            name="Remote Code Execution",
            description="Buffer overflow in HTTP request parsing",
            severity=Severity.CRITICAL,
            cve="CVE-2021-12345",
            cwe="CWE-120",
            trending=True
        )
        ```
    """

    technology = models.ForeignKey(
        Technology,
        related_name="vulnerability",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    port = models.ForeignKey(
        Port,
        related_name="vulnerability",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    name = models.TextField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.IntegerField(choices=Severity.choices, default=Severity.MEDIUM)
    cve = models.TextField(max_length=20, blank=True, null=True)
    cwe = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    trending = models.BooleanField(default=False)

    unique_fields = ["technology", "port", "name", "cve"]
    _filters = [
        Finding.Filter(Severity, "severity"),
        Finding.Filter(str, "cve", contains=True, processor=lambda c: c.lower()),
        Finding.Filter(str, "cwe", contains=True, processor=lambda c: c.lower()),
    ]
    _parse_mapping = {InputKeyword.CVE: "cve"}
    _parse_dependencies = ["technology", "port"]
    _defectdojo_finding_mapping = {
        "title": "name",
        "description": "description",
        "severity": "severity",
        "cve": "cve",
        "cwe": lambda instance: int(instance.cwe.split("-", 1)[1]) if instance.cwe else None,
        "references": "reference",
    }


class Exploit(TriageFinding):
    """Model representing available exploits for vulnerabilities and technologies.

    Represents publicly available exploit code, proof-of-concept scripts, and exploit
    references that target identified vulnerabilities and technologies. Exploit findings
    enable security teams to assess real-world impact potential and prioritize remediation
    efforts based on weaponized threat availability and exploitation complexity.

    Attributes:
        vulnerability (ForeignKey): Target vulnerability for this exploit (optional relationship)
        technology (ForeignKey): Affected technology component (optional relationship)
        title (TextField): Exploit name or descriptive title (max 100 characters)
        edb_id (IntegerField): Exploit Database unique identifier (optional)
        reference (TextField): Exploit source URL or documentation link (optional, max 250 characters)

    Example:
        Create an exploit finding linked to a vulnerability:

        ```python
        exploit = Exploit.objects.create(
            vulnerability=rce_vuln,
            title="Remote Command Execution via Buffer Overflow",
            edb_id=12345,
            reference="https://www.exploit-db.com/exploits/12345"
        )
        ```
    """

    vulnerability = models.ForeignKey(
        Vulnerability,
        related_name="exploit",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    technology = models.ForeignKey(
        Technology,
        related_name="exploit",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    title = models.TextField(max_length=100)
    edb_id = models.IntegerField(blank=True, null=True)  # Id in Exploit-DB
    reference = models.TextField(max_length=250, blank=True, null=True)

    unique_fields = ["vulnerability", "technology", "edb_id", "reference"]
    _parse_mapping = {InputKeyword.EXPLOIT: "title"}
    _parse_dependencies = ["vulnerability", "technology"]
    _defectdojo_finding_mapping = {
        "title": lambda instance: f"Exploit {instance.edb_id} found" if instance.edb_id else "Exploit found",
        "description": "title",
        "severity": lambda instance: instance.vulnerability.severity if instance.vulnerability else Severity.MEDIUM,
        "references": "reference",
    }

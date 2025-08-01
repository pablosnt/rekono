"""Django models for security findings.

This module defines the core data models for representing security findings
discovered during security assessments. Each model represents a different type
of security-related information, from basic host discovery to detailed
vulnerability information.

The models follow a hierarchical structure where findings can be related to
each other (e.g., a Port belongs to a Host, a Vulnerability can be associated
with a Technology or Port). This allows for comprehensive security analysis
and reporting.
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
    """Open Source Intelligence findings.

    Represents information discovered through open source intelligence
    gathering techniques, such as IP addresses, domains, emails, etc.

    Attributes:
        data: The actual OSINT data discovered (IP, domain, email, etc.)
        data_type: The type of OSINT data (IP, Domain, Email, etc.)
        source: The source where this OSINT data was found
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
        """Parse OSINT data for further processing.

        Only IP and Domain OSINT data types can be parsed to be
        used from tool executions.

        Args:
            accumulated: Previously accumulated parsing data.

        Returns:
            Dictionary with parsed data for target creation.
        """
        return super().parse(accumulated) if self.data_type in [OSINTDataType.IP, OSINTDataType.DOMAIN] else {}


class Host(Finding):
    """Discovered network hosts.

    Represents network hosts discovered during security assessments,
    including their IP addresses, domain names, operating systems,
    and geolocation information.

    Attributes:
        ip: The IP address of the discovered host
        domain: Associated domain name (if any)
        os: Full operating system specification
        os_type: Categorized operating system type
        country: Country where the host is located
        city: City where the host is located
        latitude: Geographic latitude coordinate
        longitude: Geographic longitude coordinate
    """

    ip = models.TextField(max_length=30)
    domain = models.TextField(max_length=500, blank=True, null=True)
    # OS full specification
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.TextField(max_length=10, choices=HostOS.choices, default=HostOS.OTHER)
    # Geolocation
    country = models.TextField(max_length=100, blank=True, null=True)
    city = models.TextField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

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
    """Network ports discovered on hosts.

    Represents network ports found on discovered hosts, including
    their status, protocol, and associated services.

    Attributes:
        host: The host this port belongs to
        port: The port number
        status: Current status of the port (open, closed, filtered, etc.)
        protocol: Transport protocol (TCP/UDP)
        service: Service running on this port (if identified)
    """

    host = models.ForeignKey(Host, related_name="port", on_delete=models.DO_NOTHING, blank=True, null=True)
    port = models.IntegerField()  # Port number
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
        """Parse port information for further processing.

        Parse port information to enable more detailed
        port-specific analysis and targeting.

        Args:
            accumulated: Previously accumulated parsing data.

        Returns:
            Dictionary with parsed port data.
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
    """Paths discovered on services.

    Represents web paths, API endpoints, or file shares discovered
    during web application scanning or directory enumeration.

    Attributes:
        port: The port/service where this path was discovered
        path: The actual path or endpoint
        status: HTTP status code or response status
        extra_info: Additional information about the path
        type: Type of path (endpoint or share)
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
        """Clean a path value for comparison operations.

        Args:
            value: The path value to clean.

        Returns:
            Cleaned path string for comparison.
        """
        if len(value) > 1:
            value = self.clean_path(value)
            if value is None:
                value = "/"
            elif value[-1] != "/":
                value += "/"
        return value

    def filter(self, input: Any, target: Target | None = None) -> bool:
        """Filter paths based on input criteria.

        Overrides the base filter method to filter paths based on
        target port paths.

        Args:
            input: The input value to filter against.
            target: Optional target for context.

        Returns:
            True if the path matches the filter criteria.
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
    """Technologies discovered on services.

    Represents software technologies, frameworks, and applications
    discovered during service enumeration and fingerprinting.

    Attributes:
        port: The port where this technology was discovered
        name: Name of the technology
        version: Version of the technology (if identified)
        description: Additional description or details
        reference: Reference link or documentation
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
    """Credentials discovered during security assessments.

    Represents usernames, passwords, API keys, and other authentication
    credentials found during security testing.

    Attributes:
        technology: The technology where credentials were found
        email: Email address (if applicable)
        username: Username or account identifier
        secret: Password, API key, or other secret
        context: Additional context about where/how credentials were found
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
    """Security vulnerabilities discovered during assessments.

    Represents security vulnerabilities found in applications, services,
    or systems.

    Attributes:
        technology: The technology where the vulnerability was found
        port: The port where the vulnerability was discovered
        name: Name or title of the vulnerability
        description: Detailed description of the vulnerability
        severity: Severity level of the vulnerability
        cve: CVE identifier (if applicable)
        cwe: CWE identifier (if applicable)
        reference: Reference link or documentation
        trending: Whether this vulnerability is currently trending
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
    """Exploits available for vulnerabilities.

    Represents exploit code, proof-of-concept scripts, or exploit
    references available for discovered vulnerabilities or technologies.

    Attributes:
        vulnerability: The vulnerability this exploit targets
        technology: The technology this exploit affects
        title: Title or name of the exploit
        edb_id: Exploit-DB identifier (if available)
        reference: Reference link to the exploit
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

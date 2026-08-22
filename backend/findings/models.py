"""Models of the findings that the tools discover.

The findings are chained by foreign keys following the order in which they are
discovered, from the OSINT data to the exploits, so the deeper ones can be used as
input for the tools and can be deduplicated within the branch they belong to.
"""

from typing import Any

from django.db import models

from executions.models import Execution
from findings.enums import (
    HostOS,
    OSINTDataType,
    PathType,
    PortStatus,
    Severity,
    TransportProtocol,
)
from findings.framework.models import Finding, HacktricksFinding, TriageFinding
from framework.enums import InputKeyword
from target_ports.models import TargetPort
from targets.enums import TargetType
from targets.models import Target


class OSINT(TriageFinding):
    """Data found on public sources during the passive reconnaissance.

    Attributes:
        data: The discovered data, whose meaning depends on its type.
        data_type: What the data is, from IP addresses to user names.
        source: Public source where the data was found.
    """

    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=OSINTDataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)

    _unique_fields = [Finding.UniqueField("data", ignore_case=True), Finding.UniqueField("data_type")]
    _parse_mapping = {
        InputKeyword.TARGET: "data",
        InputKeyword.HOST: "data",
        InputKeyword.URL: lambda instance, task: instance.get_url(instance.data, task=task),
    }
    _defectdojo_finding_mapping = {
        "title": lambda instance: f"{instance.data_type} found on public sources",
        "description": lambda instance: "\n".join(
            [f"{k}: {v}" for k, v in [("Data", instance.data), ("Source", instance.source)] if v]
        ),
        "severity": Severity.LOW,
    }

    def parse(self, task: Any, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get the tool arguments that this finding provides.

        Args:
            task: Task of the execution, forwarded to the base implementation.
            accumulated: Keywords already provided by the other inputs of the same
              execution.

        Returns:
            The arguments of the base implementation, or an empty dict for the
            data types that can't be scanned, like the user names or the emails.
        """
        return super().parse(task, accumulated) if self.data_type in [OSINTDataType.IP, OSINTDataType.DOMAIN] else {}


class Host(HacktricksFinding):
    """Host found in the network, identified by its IP address.

    Attributes:
        ip: IPv4 or IPv6 address that identifies the host.
        domain: Domain name that resolves to the IP address.
        os: Operating system as the tools report it, with its version.
        os_type: Operating system family, used to select the tools to run.
        country: Country where the IP address is located.
        city: City where the IP address is located.
        latitude: Latitude of the IP address location.
        longitude: Longitude of the IP address location.
        reputation: VirusTotal reputation score of the IP address.
        malicious_analysis: VirusTotal engines that flagged the host as malicious.
        suspicious_analysis: VirusTotal engines that flagged the host as suspicious.
        total_analysis: VirusTotal engines that analyzed the host.
        whois: WHOIS record of the IP address, as the registry returns it.
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
    malicious_analysis = models.IntegerField(blank=True, null=True)
    suspicious_analysis = models.IntegerField(blank=True, null=True)
    total_analysis = models.IntegerField(blank=True, null=True)
    whois = models.TextField(blank=True, null=True)

    _unique_fields = [Finding.UniqueField("ip")]
    _filters = [Finding.Filter(TargetType, "ip", processor=lambda a: Target.get_type(a))]
    _parse_mapping = {
        InputKeyword.TARGET: "ip",
        InputKeyword.HOST: "ip",
        InputKeyword.URL: lambda instance, task: instance.get_url(instance.ip, task=task),
    }
    _defectdojo_finding_mapping = {
        "title": "Host discovered",
        "description": lambda instance: (
            "\n".join(
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
                        ("Reputation", instance.reputation),
                        ("Malicious Analysis", instance.malicious_analysis),
                        ("Suspicious Analysis", instance.suspicious_analysis),
                        ("Total Analysis", instance.total_analysis),
                    ]
                    if v
                ]
            )
            + (f"\nWHOIS:\n{instance.whois}" if instance.whois else "")
        ),
        "severity": Severity.INFO,
    }


class Port(HacktricksFinding):
    """Port found in a host, with the service that listens on it.

    Attributes:
        host: Host where the port was found.
        port: Port number.
        status: State of the port, which is open unless a tool reports otherwise.
        protocol: Transport protocol where the port was found.
        service: Service that listens on the port, as the tools identify it.
    """

    host = models.ForeignKey(Host, related_name="port", on_delete=models.DO_NOTHING, blank=True, null=True)
    port = models.IntegerField()
    status = models.TextField(max_length=17, choices=PortStatus.choices, default=PortStatus.OPEN)
    protocol = models.TextField(max_length=5, choices=TransportProtocol.choices, blank=True, null=True)
    service = models.TextField(max_length=50, blank=True, null=True)

    _unique_fields = [
        Finding.UniqueField("host"),
        Finding.UniqueField("port"),
        Finding.UniqueField("protocol", match_null_and_empty=True),
    ]
    _root_findings = ("host",)
    # _parse_dependencies is left empty on purpose: parsing the host again would rebuild the
    # URL that this port already provides, and that means probing it again
    _parse_mapping = {InputKeyword.PORT: "port", InputKeyword.PORTS: lambda instance, task: [instance.port]}
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
        "endpoints": lambda instance: [path.defectdojo_endpoint() for path in instance.path.all()],
    }
    _filters = [
        Finding.Filter(int, "port"),
        Finding.Filter(str, "service", contains=True, processor=lambda s: s.lower()),
    ]

    def parse(self, task: Any, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get the tool arguments that this finding provides.

        Args:
            task: Task of the execution, forwarded to the base implementation.
            accumulated: Keywords already provided by the other inputs of the same
              execution.

        Returns:
            The arguments of the base implementation, plus the ones that combine
            the port with its host, which are only available if the host is known.
        """
        output = super().parse(task, accumulated)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ",".join(
            [str(p) for p in output.get(InputKeyword.PORTS.name.lower()) or []]
        )
        if self.host:
            output.update(
                {
                    InputKeyword.TARGET.name.lower(): f"{self.host.ip}:{self.port}",
                    InputKeyword.HOST.name.lower(): self.host.ip,
                }
            )
            url = self.get_url(self.host.ip, self.port, task=task)
            if url is not None:
                output[InputKeyword.URL.name.lower()] = url
        return output


class Path(Finding):
    """Path found in a port, like a web endpoint or a shared resource.

    Attributes:
        port: Port where the path was found.
        path: Location of the path within the service.
        status: HTTP status code returned by the path.
        extra_info: Extra data about the path reported by the tool that found it.
        type: Kind of path, which depends on the protocol where it was found.
    """

    port = models.ForeignKey(Port, related_name="path", on_delete=models.DO_NOTHING, blank=True, null=True)
    path = models.TextField(max_length=500)
    status = models.IntegerField(blank=True, null=True)
    extra_info = models.TextField(max_length=100, blank=True, null=True)
    type = models.TextField(choices=PathType.choices, default=PathType.ENDPOINT)

    _unique_fields = [Finding.UniqueField("port"), Finding.UniqueField("path")]
    _root_findings = ("port",)
    _filters = [
        Finding.Filter(PathType, "type"),
        Finding.Filter(int, "status"),
        Finding.Filter(str, "path", contains=True, processor=lambda p: p.lower()),
    ]
    _parse_mapping = {
        InputKeyword.ENDPOINT: lambda instance, task: instance.clean_path(instance.path),
        InputKeyword.URL: lambda instance, task: (
            (instance.get_url(instance.port.host.ip, instance.port.port, instance.clean_path(instance.path), task=task))
            if instance.port and instance.port.host
            else None
        ),
    }
    _parse_dependencies = ["port"]
    _defectdojo_endpoint_mapping = {
        "protocol": lambda instance: instance.port.service if instance.port else None,
        "host": lambda instance: instance.port.host.ip if instance.port and instance.port.host else None,
        "port": lambda instance: instance.port.port if instance.port else None,
        "path": "path",
    }

    def _clean_comparison_path(self, value: str) -> str:
        """Get a path with a trailing slash, so two paths can be compared.

        Args:
            value: Path as it was reported or configured.

        Returns:
            The path with a leading and a trailing slash, so a prefix comparison
            can't match half of a directory name.
        """
        if len(value) > 1:
            value = self.clean_path(value)
            if value is None:
                value = "/"
            elif value[-1] != "/":
                value += "/"
        return value

    def filter(self, argument_input: Any, target: Target | None = None) -> bool:
        """Check if this finding can be used as input for an argument.

        Args:
            argument_input: Tool input whose filter conditions must be matched.
            target: Target of the execution, whose target ports may restrict the
              paths that can be scanned.

        Returns:
            Whether the path matches the argument input and, if the target defines
            a path for this port, whether it's inside that path.
        """
        filter = super().filter(argument_input, target)
        if self.port:
            target_port = TargetPort.objects.filter(target=target, port=self.port.port).first()
            if target_port and target_port.path:
                # If there is a target port with path, only paths within it will be considered
                filter = filter and self._clean_comparison_path(self.path).startswith(
                    self._clean_comparison_path(target_port.path)
                )
        return filter


class Technology(HacktricksFinding):
    """Software found in a port, with the version that it runs.

    Attributes:
        port: Port where the technology was found.
        name: Name of the technology, as the tools identify it.
        version: Version of the technology, which is often unknown.
        description: Extra data about the technology reported by the tools.
        reference: Link to the technology documentation or vendor.
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

    _unique_fields = [
        Finding.UniqueField("port"),
        Finding.UniqueField("name", ignore_case=True),
        Finding.UniqueField("version", match_null_and_empty=True, ignore_case=True),
    ]
    _root_findings = ("port",)
    _filters = [Finding.Filter(str, "name", contains=True, processor=lambda n: n.lower())]
    # Version is parsed as empty string when None, as most of the tools working from
    # technologies only require the technology name
    _parse_mapping = {
        InputKeyword.TECHNOLOGY: "name",
        InputKeyword.VERSION: lambda instance, task: instance.version or "",
    }
    _parse_dependencies = ["port"]
    _defectdojo_finding_mapping = {
        "title": lambda instance: f"Technology {instance.name} detected",
        "description": lambda instance: (
            (f"{instance.description}\n\n" if instance.description else "")
            + "\n".join([f"{k}: {v}" for k, v in [("Technology", instance.name), ("Version", instance.version)] if v])
        ),
        "severity": Severity.LOW,
        "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
        "references": "reference",
    }


class Credential(TriageFinding):
    """Credential exposed in a technology or in a public source.

    The three data fields are optional because a leak can expose only one of them,
    like an email address without its password.

    Attributes:
        technology: Technology where the credential was exposed.
        email: Email address that identifies the account.
        username: User name that identifies the account.
        secret: Password, API key, or any other secret of the account.
        context: Where the credential was found and how.
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
    secret = models.TextField(max_length=300, blank=True, null=True)
    context = models.TextField(max_length=300, blank=True, null=True)

    _unique_fields = [
        Finding.UniqueField("technology"),
        Finding.UniqueField("email", ignore_case=True),
        Finding.UniqueField("username"),
        Finding.UniqueField("secret"),
    ]
    _root_findings = ("technology",)
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
    """Vulnerability found in a technology or in a port.

    Most of the fields are filled by the CVE providers instead of by the tool that
    discovered the vulnerability, so they are only available for the vulnerabilities
    with a known identifier.

    Attributes:
        technology: Technology where the vulnerability was found.
        port: Port where the vulnerability was found, if the technology is unknown.
        name: Name of the vulnerability, as the tools report it.
        description: Explanation of the vulnerability and its impact.
        severity: Risk of the vulnerability, used to sort and to alert about it.
        cvss_version: CVSS version used to calculate the score.
        cvss_vector: CVSS vector with the metrics behind the score.
        cvss_base_score: CVSS base score of the vulnerability.
        cve: CVE identifier of the vulnerability.
        euvd_id: ENISA EUVD identifier of the vulnerability.
        ghsa_id: GitHub Security Advisory identifier of the vulnerability.
        osv_generic_id: OSV identifier for the ecosystems without their own one.
        cwes: CWE identifiers of the weaknesses behind the vulnerability.
        epss_score: Probability of the vulnerability being exploited in 30 days.
        epss_percentile: Position of the EPSS score among all the scored CVEs.
        remediation: Steps to fix or to mitigate the vulnerability.
        reference: Link to the advisory or to the vulnerability documentation.
        trending: Whether the vulnerability is being discussed in social networks.
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
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    severity = models.IntegerField(choices=Severity.choices, default=Severity.MEDIUM)
    cvss_version = models.TextField(max_length=3, blank=True, null=True)
    cvss_vector = models.TextField(max_length=200, blank=True, null=True)
    cvss_base_score = models.FloatField(blank=True, null=True)
    cve = models.TextField(max_length=30, blank=True, null=True)
    euvd_id = models.TextField(max_length=30, blank=True, null=True)
    ghsa_id = models.TextField(max_length=30, blank=True, null=True)
    osv_generic_id = models.TextField(max_length=100, blank=True, null=True)
    cwes = models.JSONField(default=list, blank=True)
    epss_score = models.FloatField(blank=True, null=True)
    epss_percentile = models.FloatField(blank=True, null=True)
    remediation = models.TextField(blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    trending = models.BooleanField(default=False)

    _unique_fields = [
        Finding.UniqueField("technology"),
        Finding.UniqueField("port"),
        Finding.UniqueField("name", ignore_case=True),
        Finding.UniqueField("cve", ignore_case=True),
    ]
    # Ordered by priority for deduplication: technology is a deeper root than port
    _root_findings = ("technology", "port")
    _filters = [Finding.Filter(str, "cve", contains=True, processor=lambda c: c.lower())]
    _parse_mapping = {InputKeyword.CVE: "cve"}
    _parse_dependencies = ["technology", "port"]
    _defectdojo_finding_mapping = {
        "title": "name",
        "description": "description",
        "severity": "severity",
        "cve": "cve",
        "cwe": lambda instance: int(instance.cwes[-1].split("-", 1)[1]) if instance.cwes else None,
        "cvssv3": lambda instance: (
            instance.cvss_vector if instance.cvss_version and instance.cvss_version.startswith("3") else None
        ),
        "cvssv3_score": lambda instance: (
            instance.cvss_base_score if instance.cvss_version and instance.cvss_version.startswith("3") else None
        ),
        "cvssv4": lambda instance: (
            instance.cvss_vector if instance.cvss_version and instance.cvss_version.startswith("4") else None
        ),
        "cvssv4_score": lambda instance: (
            instance.cvss_base_score if instance.cvss_version and instance.cvss_version.startswith("4") else None
        ),
        "mitigation": "remediation",
        "references": "reference",
    }

    @classmethod
    def _find_duplicate(cls, execution: Execution, fields: dict[str, Any]) -> "Vulnerability | None":
        """Find an existing vulnerability that duplicates the incoming one.

        Args:
            execution: Execution that discovered the incoming vulnerability.
            fields: Values that the incoming vulnerability would be created with.

        Returns:
            The vulnerability with the same identity, which is the CVE or the name
            when no CVE is known, found in the same technology or port within the
            target, or None if this vulnerability wasn't discovered before.
        """
        technology = fields.get("technology")
        identity = (
            models.Q(cve__iexact=fields["cve"]) if fields.get("cve") else models.Q(name__iexact=fields.get("name"))
        )
        if technology:
            search = cls.objects.filter(
                identity, executions__task__target=execution.task.target, technology=technology
            ).order_by("id")
            if search.exists():
                return search.first()
        port = fields.get("port") or (technology.port if technology else None)
        # A vulnerability found in a port also matches the ones found in the technologies of that
        # port, so a tool that doesn't detect the technology can complete a previous finding
        return (
            cls.objects.filter(
                identity,
                models.Q(port=port) | models.Q(technology__port=port),
                executions__task__target=execution.task.target,
            )
            .order_by("id")
            .first()
        )


class Exploit(TriageFinding):
    """Public exploit that targets a vulnerability or a technology.

    Attributes:
        vulnerability: Vulnerability that the exploit takes advantage of.
        technology: Technology that the exploit targets, if the vulnerability is unknown.
        title: Name of the exploit, as its source reports it.
        edb_id: Exploit Database identifier of the exploit.
        reference: Link to the exploit code or to its documentation.
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
    edb_id = models.IntegerField(blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    _unique_fields = [
        Finding.UniqueField("vulnerability"),
        Finding.UniqueField("technology"),
        Finding.UniqueField("edb_id", match_null_and_empty=True),
        Finding.UniqueField("reference", match_null_and_empty=True),
    ]
    # Ordered by priority for deduplication: vulnerability is a deeper root than technology
    _root_findings = ("vulnerability", "technology")
    _parse_mapping = {InputKeyword.EXPLOIT: "title"}
    _parse_dependencies = ["vulnerability", "technology"]
    _defectdojo_finding_mapping = {
        "title": lambda instance: f"Exploit {instance.edb_id} found" if instance.edb_id else "Exploit found",
        "description": "title",
        "severity": lambda instance: instance.vulnerability.severity if instance.vulnerability else Severity.MEDIUM,
        "references": "reference",
    }

    @classmethod
    def _find_duplicate(cls, execution: Execution, fields: dict[str, Any]) -> "Exploit | None":
        """Find an existing exploit that duplicates the incoming one.

        Args:
            execution: Execution that discovered the incoming exploit.
            fields: Values that the incoming exploit would be created with.

        Returns:
            The exploit with the same identifier and reference found in the closest
            place to the incoming one within the target, or None if this exploit
            wasn't discovered before.
        """
        query = models.Q(executions__task__target=execution.task.target)
        for unique_field in cls._unique_fields:
            if unique_field.field in cls._root_findings:
                continue
            field_query = cls._get_deduplication_field_query(unique_field, fields.get(unique_field.field))
            if field_query is not None:
                query &= field_query
        # The exploit is searched from the most specific place where it can be found to the least
        # one, so the exploits of the same vulnerability are always preferred over the ones that
        # only share the port where they were found
        vulnerability = fields.get("vulnerability")
        if vulnerability:
            search = cls.objects.filter(query, vulnerability=vulnerability).order_by("id")
            if search.exists():
                return search.first()
            port = vulnerability.port
            if vulnerability.technology:
                search = cls.objects.filter(query, technology=vulnerability.technology).order_by("id")
                if search.exists():
                    return search.first()
                port = vulnerability.technology.port
            # The exploits for different vulnerabilities must not match
            return cls.objects.filter(query, models.Q(technology__port=port)).order_by("id").first()
        technology = fields.get("technology")
        if technology:
            search = cls.objects.filter(
                query, models.Q(technology=technology) | models.Q(vulnerability__technology=technology)
            ).order_by("id")
            if search.exists():
                return search.first()
            return (
                cls.objects.filter(
                    query,
                    models.Q(technology__port=technology.port)
                    | models.Q(vulnerability__technology__port=technology.port)
                    | models.Q(vulnerability__port=technology.port),
                )
                .order_by("id")
                .first()
                if technology.port
                else None
            )
        return None

from typing import Any

from django.db import models
from django.utils import timezone
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
from platforms.defectdojo.models import DefectDojoSettings
from target_ports.models import TargetPort
from targets.enums import TargetType
from targets.models import Target

# Create your models here.


class OSINT(TriageFinding):
    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=OSINTDataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)

    unique_fields = ["data", "data_type"]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        return (
            {
                InputKeyword.TARGET.name.lower(): self.data,
                InputKeyword.HOST.name.lower(): self.data,
                InputKeyword.URL.name.lower(): self._get_url(self.data),
            }
            if self.data_type in [OSINTDataType.IP, OSINTDataType.DOMAIN]
            else {}
        )

    def defectdojo(self) -> dict[str, Any]:
        return {
            "title": f"{self.data_type} found using OSINT techniques",
            "description": self.data,
            "severity": Severity.MEDIUM,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        return self.data


class Host(Finding):
    address = models.TextField(max_length=30)
    # OS full specification
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.TextField(
        max_length=10, choices=HostOS.choices, default=HostOS.OTHER
    )

    unique_fields = ["address"]
    filters = [Finding.Filter(TargetType, "address", lambda a: Target.get_type(a))]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        return {
            InputKeyword.TARGET.name.lower(): self.address,
            InputKeyword.HOST.name.lower(): self.address,
            InputKeyword.URL.name.lower(): self._get_url(self.address),
        }

    def defectdojo(self) -> dict[str, Any]:
        return {
            "title": "Host discovered",
            "description": " - ".join(
                [field for field in [self.address, self.os_type] if field]
            ),
            "severity": Severity.INFO,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        return self.address


class Port(Finding):
    host = models.ForeignKey(
        Host, related_name="port", on_delete=models.DO_NOTHING, blank=True, null=True
    )
    port = models.IntegerField()  # Port number
    status = models.TextField(
        max_length=15, choices=PortStatus.choices, default=PortStatus.OPEN
    )
    protocol = models.TextField(
        max_length=5, choices=Protocol.choices, blank=True, null=True
    )
    service = models.TextField(max_length=50, blank=True, null=True)

    unique_fields = ["host", "port", "protocol"]
    filters = [
        Finding.Filter(int, "port"),
        Finding.Filter(str, "service", contains=True, processor=lambda s: s.lower()),
    ]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        ports = (
            [self.port]
            if not accumulated
            else accumulated.get(InputKeyword.PORTS.name.lower(), []) + [self.port]
        )
        output = {
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): ports,
            InputKeyword.PORTS_COMMAS.name.lower(): ",".join([str(p) for p in ports]),
        }
        if self.host:
            output.update(
                {
                    InputKeyword.TARGET.name.lower(): f"{self.host.address}:{self.port}",
                    InputKeyword.HOST.name.lower(): self.host.address,
                    InputKeyword.URL.name.lower(): self._get_url(
                        self.host.address, self.port
                    ),
                }
            )
        return output

    def defectdojo(self) -> dict[str, Any]:
        description = f"Port: {self.port}\nStatus: {self.status}\nProtocol: {self.protocol}\nService: {self.service}"
        return {
            "title": "Port discovered",
            "description": (
                f"Host: {self.host.address}\n{description}"
                if self.host
                else description
            ),
            "severity": Severity.INFO,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        return f"{f'{self.host.__str__()} - ' if self.host else ''}{self.port}"


class Path(Finding):
    port = models.ForeignKey(
        Port, related_name="path", on_delete=models.DO_NOTHING, blank=True, null=True
    )
    path = models.TextField(max_length=500)
    # Status received for that path. Probably HTTP status
    status = models.IntegerField(blank=True, null=True)
    extra_info = models.TextField(max_length=100, blank=True, null=True)
    # Path type depending on the protocol where it's found
    type = models.TextField(choices=PathType.choices, default=PathType.ENDPOINT)

    unique_fields = ["port", "path"]
    filters = [
        Finding.Filter(PathType, "type"),
        Finding.Filter(int, "status"),
        Finding.Filter(str, "path", contains=True, processor=lambda p: p.lower()),
    ]

    def _clean_comparison_path(self, value: str) -> str:
        if len(value) > 1:
            value = self._clean_path(value)
            if value[-1] != "/":
                value += "/"
        return value

    def filter(self, input: Any, target: Target = None) -> bool:
        filter = super().filter(input, target)
        if self.port:
            target_port = TargetPort.objects.filter(
                target=target, port=self.port.port
            ).first()
            if target_port and target_port.path:
                filter = filter and self._clean_comparison_path(self.path).startswith(
                    self._clean_comparison_path(target_port.path)
                )
        return filter

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        path = self._clean_path(self.path)
        output = (
            {
                **self.port.parse(accumulated),
                InputKeyword.URL.name.lower(): self._get_url(
                    self.port.host.address, self.port.port, path
                ),
            }
            if self.port
            else {}
        )
        return {
            **output,
            InputKeyword.ENDPOINT.name.lower(): path,
        }

    def defectdojo_endpoint(self, target: Target) -> dict[str, Any]:
        return {
            "protocol": self.port.service if self.port else None,
            "host": (
                self.port.host.address
                if self.port and self.port.host
                else target.target
            ),
            "port": self.port.port if self.port else None,
            "path": self.path,
        }

    def defectdojo(self) -> dict[str, Any]:
        description = f"Path: {self.path}\nType: {self.type}"
        for key, value in [("Status", self.status), ("Info", self.extra_info)]:
            if value:
                description = f"{description}\n{key}: {value}"
        if self.port:
            description = f"Port: {self.port.port}\n{description}"
            if self.port.host:
                description = f"Host: {self.port.host.address}\n{description}"
        return {
            "title": "Path discovered",
            "description": description,
            "severity": Severity.INFO,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        return f"{f'{self.port.__str__()} - ' if self.port else ''}{self.path}"


class Technology(Finding):
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
    filters = [
        Finding.Filter(str, "name", contains=True, processor=lambda n: n.lower())
    ]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = {InputKeyword.TECHNOLOGY.name.lower(): self.name}
        if self.version:
            output.update({InputKeyword.VERSION.name.lower(): self.version})
        if self.port:
            output.update(self.port.parse(accumulated))
        return output

    def defectdojo(self) -> dict[str, Any]:
        description = f"Technology: {self.name}\nVersion: {self.version}"
        return {
            "title": f"Technology {self.name} detected",
            "description": (
                f"{description}\nDetails: {self.description}"
                if self.description
                else description
            ),
            "severity": Severity.LOW,
            "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            "references": self.reference,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        return f"{f'{self.port.__str__()} - ' if self.port else ''}{self.name}"


class Credential(TriageFinding):
    """Credential model."""

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

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        output = self.technology.parse(accumulated) if self.technology else {}
        for key, field in [
            (InputKeyword.EMAIL.name.lower(), self.email),
            (InputKeyword.USERNAME.name.lower(), self.username),
            (InputKeyword.SECRET.name.lower(), self.secret),
        ]:
            if field:
                output[key] = field
        return output

    def defectdojo(self) -> dict[str, Any]:
        return {
            "title": "Credentials exposure",
            "description": " - ".join(
                [field for field in [self.email, self.username, self.secret] if field]
            ),
            "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            "severity": Severity.HIGH,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        values = [self.technology.__str__()] if self.technology else []
        values += [field for field in [self.email, self.username, self.secret] if field]
        return " - ".join(values)


class Vulnerability(TriageFinding):
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
    osvdb = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    trending = models.BooleanField(default=False)

    unique_fields = ["technology", "port", "name", "cve"]
    filters = [
        Finding.Filter(Severity, "severity"),
        Finding.Filter(str, "cve", contains=True, processor=lambda c: c.lower()),
        Finding.Filter(str, "cwe", contains=True, processor=lambda c: c.lower()),
    ]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        output = {InputKeyword.CVE.name.lower(): self.cve}
        if self.technology:
            output.update(self.technology.parse(accumulated))
        elif self.port:
            output.update(self.port.parse(accumulated))
        return output

    def defectdojo(self) -> dict[str, Any]:
        return {
            "title": self.name,
            "description": self.description,
            "severity": self.severity,
            "cve": self.cve,
            "cwe": int(self.cwe.split("-", 1)[1]) if self.cwe else None,
            "references": self.reference,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        return f"{f'{(self.technology or self.port).__str__()} - ' if self.technology or self.port else ''}{self.name}{f' - {self.cve}' if self.cve else ''}"


class Exploit(TriageFinding):
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

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        output = {InputKeyword.EXPLOIT.name.lower(): self.title}
        if self.vulnerability:
            output.update(self.vulnerability.parse(accumulated))
        elif self.technology:
            output.update(self.technology.parse(accumulated))
        return output

    def defectdojo(self) -> dict[str, Any]:
        return {
            "title": f"Exploit {self.edb_id} found" if self.edb_id else "Exploit found",
            "description": self.title,
            "severity": (
                self.vulnerability.severity if self.vulnerability else Severity.MEDIUM
            ),
            "references": self.reference,
            "date": (
                self.executions.order_by("-end").first().end or timezone.now()
            ).strftime(DefectDojoSettings.objects.first().date_format),
        }

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{f'{(self.vulnerability or self.technology).__str__()} - ' if self.vulnerability or self.technology else ''}{self.title}"

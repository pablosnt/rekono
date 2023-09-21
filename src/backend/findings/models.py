from typing import Any, Dict

from django.db import models
from findings.enums import (
    HostOS,
    OSINTDataType,
    PathType,
    PortStatus,
    Protocol,
    Severity,
)
from findings.framework.models import Finding
from framework.enums import InputKeyword
from targets.enums import TargetType
from targets.models import Target

# Create your models here.


class OSINT(Finding):
    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=OSINTDataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        if self.data_type in [OSINTDataType.IP, OSINTDataType.DOMAIN]:
            return {
                InputKeyword.TARGET.name.lower(): self.data,
                InputKeyword.HOST.name.lower(): self.data,
                InputKeyword.URL.name.lower(): self._get_url(self.data),
            }
        return {}

    def defect_dojo(self) -> Dict[str, Any]:
        return {
            "title": f"{self.data_type} found using OSINT techniques",
            "description": self.data,
            "severity": str(Severity.MEDIUM),
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
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

    filters = [Finding.Filter(TargetType, "address", lambda a: Target.get_type(a))]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        return {
            InputKeyword.TARGET.name.lower(): self.address,
            InputKeyword.HOST.name.lower(): self.address,
            InputKeyword.URL.name.lower(): self._get_url(self.address),
        }

    def defect_dojo(self) -> Dict[str, Any]:
        return {
            "title": "Host discovered",
            "description": " - ".join(
                [field for field in [self.address, self.os_type] if field]
            ),
            "severity": str(Severity.INFO),
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
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

    filters = [
        Finding.Filter(int, "port"),
        Finding.Filter(str, "service", contains=True, processor=lambda s: s.lower()),
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        ports = (
            [self.port]
            if not accumulated or InputKeyword.PORTS.name.lower() not in accumulated
            else [self.port] + accumulated[InputKeyword.PORTS.name.lower()]
        )
        output = {
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): ports,
            InputKeyword.PORTS_COMMAS.name.lower(): [str(p) for p in ports],
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

    def defect_dojo(self) -> Dict[str, Any]:
        description = f"Port: {self.port}\nStatus: {self.status}\nProtocol: {self.protocol}\nService {self.service}"
        return {
            "title": "Port discovered",
            "description": f"Host: {self.host.address}\n{description}"
            if self.host
            else description,
            "severity": str(Severity.INFO),
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
        }

    def __str__(self) -> str:
        values = [self.host.__str__()] if self.host else []
        values.append(str(self.port))
        return " - ".join(values)


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

    filters = [
        Finding.Filter(PathType, "type"),
        Finding.Filter(int, "status"),
        Finding.Filter(str, "path", contains=True, processor=lambda p: p.lower()),
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        output = self.port.parse(accumulated) if self.port else {}
        output[InputKeyword.ENDPOINT.name.lower()] = self.path
        if self.port:
            output[InputKeyword.URL.name.lower()] = self._get_url(
                self.port.host.address, self.port.port, self.path
            )
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        return {
            "protocol": self.port.service if self.port else None,
            "host": self.port.host.address if self.port else None,
            "port": self.port.port if self.port else None,
            "path": self.path,
        }

    def __str__(self) -> str:
        values = [self.port.__str__()] if self.port else []
        values.append(str(self.path))
        return " - ".join(values)


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
    related_to = models.ForeignKey(
        "Technology",
        related_name="related_technologies",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    reference = models.TextField(max_length=250, blank=True, null=True)

    filters = [
        Finding.Filter(str, "name", contains=True, processor=lambda n: n.lower())
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        output = self.port.parse(accumulated) if self.port else {}
        output.update({InputKeyword.TECHNOLOGY.name.lower(): self.name})
        if self.version:
            output.update({InputKeyword.VERSION.name.lower(): self.version})
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        description = f"Technology: {self.name}\nVersion: {self.version}"
        return {
            "title": f"Technology {self.name} detected",
            "description": f"{description}\nDetails: {self.description}"
            if self.description
            else description,
            "severity": str(Severity.LOW),
            "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            "references": self.reference,
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
        }

    def __str__(self) -> str:
        values = [self.port.__str__()] if self.port else []
        values.append(str(self.name))
        return " - ".join(values)


class Credential(Finding):
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

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        output = self.technology.parse(accumulated) if self.technology else {}
        for key, field in [
            (InputKeyword.EMAIL.name.lower(), self.email),
            (InputKeyword.USERNAME.name.lower(), self.username),
            (InputKeyword.SECRET.name.lower(), self.secret),
        ]:
            if field:
                output[key] = field
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        return {
            "title": "Credentials exposure",
            "description": " - ".join(
                [field for field in [self.email, self.username, self.secret] if field]
            ),
            "cwe": 200,  # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            "severity": str(Severity.HIGH),
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
        }

    def __str__(self) -> str:
        values = [self.technology.__str__()] if self.technology else []
        values += [field for field in [self.email, self.username, self.secret] if field]
        return " - ".join(values)


class Vulnerability(Finding):
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
    severity = models.TextField(choices=Severity.choices, default=Severity.MEDIUM)
    cve = models.TextField(max_length=20, blank=True, null=True)
    cwe = models.TextField(max_length=20, blank=True, null=True)
    osvdb = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    filters = [
        Finding.Filter(Severity, "severity"),
        Finding.Filter(str, "cve", contains=True, processor=lambda c: c.lower()),
        Finding.Filter(str, "cwe", contains=True, processor=lambda c: c.lower()),
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        output = {InputKeyword.CVE.name.lower(): self.cve}
        if self.technology:
            output.update(self.technology.parse(accumulated))
        elif self.port:
            output.update(self.port.parse(accumulated))
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        return {
            "title": self.name,
            "description": self.description,
            "severity": Severity(self.severity).value,
            "cve": self.cve,
            "cwe": int(self.cwe.split("-", 1)[1]) if self.cwe else None,
            "references": self.reference,
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
        }

    def __str__(self) -> str:
        values = []
        if self.technology:
            values = [self.technology.__str__()]
        elif self.port:
            values = [self.port.__str__()]
        values.append(self.name)
        if self.cve:
            values.append(self.cve)
        return " - ".join(values)


class Exploit(Finding):
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

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        output = {InputKeyword.EXPLOIT.name.lower(): self.title}
        if self.vulnerability:
            output.update(self.vulnerability.parse(accumulated))
        elif self.technology:
            output.update(self.technology.parse(accumulated))
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        return {
            "title": f"Exploit {self.edb_id} found" if self.edb_id else "Exploit found",
            "description": self.title,
            "severity": Severity(self.vulnerability.severity).value
            if self.vulnerability
            else str(Severity.MEDIUM),
            "reference": self.reference,
            # TODO: Defect-Dojo
            # "date": self.last_seen.strftime(DD_DATE_FORMAT),
        }

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        values = []
        if self.vulnerability:
            values += [self.vulnerability.__str__()]
        elif self.technology:
            values += [self.technology.__str__()]
        values.append(self.title)
        return " - ".join(values)

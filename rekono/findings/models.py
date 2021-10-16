from django.db import models
from typing import Any

from executions.models import Execution
from findings.enums import Severity

# Create your models here.


class OSINT(models.Model):

    class DataType(models.IntegerChoices):
        IP = 1
        DOMAIN = 2
        URL = 3
        MAIL = 4
        LINK = 5
        ASN = 6
        USER = 7
        PASSWORD = 8

    execution = models.ForeignKey(
        Execution,
        related_name='osints',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    data = models.TextField(max_length=250)
    data_type = models.IntegerField(choices=DataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        req = self.execution.task if self.execution else None
        return hash((req, self.data, self.data_type))
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return o.execution.task == self.execution.task and o.data == self.data
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class Host(models.Model):

    class OSType(models.IntegerChoices):
        LINUX = 1
        WINDOWS = 2
        MACOS = 3
        IOS = 4
        ANDROID = 5
        SOLARIS = 6
        FREEBSD = 7
        OTHER = 8

    execution = models.ForeignKey(
        Execution,
        related_name='hosts',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    address = models.TextField(max_length=20)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.IntegerField(choices=OSType.choices, default=OSType.OTHER)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        req = self.execution.task if self.execution else None
        return hash((req, self.address))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            if o.execution and self.execution:
                return o.execution.task == self.execution.task and o.address == self.address
            else:
                return o.address == self.address
        return False
    
    def get_project(self) -> Any:
        return self.execution.task.target.project


class Enumeration(models.Model):

    class PortStatus(models.IntegerChoices):
        OPEN = 1
        OPEN_FILTERED = 2
        FILTERED = 3
        CLOSED = 4

    class Protocol(models.IntegerChoices):
        UDP = 1
        TCP = 2

    execution = models.ForeignKey(
        Execution,
        related_name='enumerations',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    host = models.ForeignKey(
        Host,
        related_name='enumerations',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    port = models.IntegerField()
    port_status = models.IntegerField(choices=PortStatus.choices, default=PortStatus.OPEN)
    protocol = models.IntegerField(choices=Protocol.choices, blank=True, null=True)
    service = models.TextField(max_length=50, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        return hash((self.host, self.port))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return o.host == self.host and o.port == self.port
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class HttpEndpoint(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='http_endpoints',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='http_endpoints',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    endpoint = models.TextField(max_length=500)
    status = models.IntegerField(blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        return hash((self.enumeration, self.endpoint))
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return o.enumeration == self.enumeration and o.endpoint == self.endpoint
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class Technology(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='technologies',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='technologies',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=100)
    version = models.TextField(max_length=100, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        return hash((self.enumeration, self.name, self.version))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                o.enumeration == self.enumeration and
                o.name == self.name and
                o.version == self.version
            )
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class Vulnerability(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='vulnerabilities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    technology = models.ForeignKey(
        Technology,
        related_name='vulnerabilities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.IntegerField(choices=Severity.choices, default=Severity.MEDIUM)
    cve = models.TextField(max_length=20, blank=True, null=True)
    osvdb = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        return hash((self.technology, self.name, self.cve))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return o.technology == self.technology and o.name == self.name and o.cve == self.cve
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class Exploit(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='exploits',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    vulnerability = models.ForeignKey(
        Vulnerability,
        related_name='exploits',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    technology = models.ForeignKey(
        Technology,
        related_name='exploits',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    checked = models.BooleanField(default=False)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __hash__(self) -> int:
        return hash((self.technology, self.vulnerability, self.name, self.reference))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                (o.technology == self.technology or o.vulnerability == self.vulnerability) and
                o.name == self.name and o.reference == self.reference
            )
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project

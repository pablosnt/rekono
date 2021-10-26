from typing import Any

from django.db import models
from executions.models import Execution
from findings.enums import DataType, OSType, PortStatus, Protocol, Severity

# Create your models here.


class Finding(models.Model):
    execution = models.ForeignKey(
        Execution,
        related_name='%(class)s',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    KEY_FIELDS = ('task')

    def __hash__(self) -> int:
        hash_fields = ()
        for field in self.KEY_FIELDS:
            if field == 'task':
                hash_fields.append(self.execution.task)
            else:
                hash_fields.append(getattr(self, field))
        return hash(hash_fields)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            equals = True
            for field in self.KEY_FIELDS:
                if field == 'task':
                    equals = equals and (self.execution.task == o.execution.task)
                else:
                    equals = equals and (getattr(self, field) == getattr(o, field))

    def get_project(self) -> Any:
        return self.execution.task.target.project


class OSINT(Finding):
    data = models.TextField(max_length=250)
    data_type = models.IntegerField(choices=DataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    KEY_FIELDS = ('task', 'data', 'data_type')    


class Host(Finding):
    address = models.TextField(max_length=20)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.IntegerField(choices=OSType.choices, default=OSType.OTHER)

    KEY_FIELDS = ('task', 'address')


class Enumeration(Finding):
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

    KEY_FIELDS = ('host', 'port')


class Endpoint(Finding):
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='endpoints',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    endpoint = models.TextField(max_length=500)
    status = models.IntegerField(blank=True, null=True)

    KEY_FIELDS = ('enumeration', 'endpoint')


class Technology(Finding):
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='technologys',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=100)
    version = models.TextField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    related_to = models.ForeignKey(
        'Technology',
        related_name='related_technologies',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    reference = models.TextField(max_length=250, blank=True, null=True)

    KEY_FIELDS = ('enumeration', 'name', 'version')


class Vulnerability(Finding):
    technology = models.ForeignKey(
        Technology,
        related_name='vulnerabilitys',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.IntegerField(choices=Severity.choices, default=Severity.MEDIUM)
    cve = models.TextField(max_length=20, blank=True, null=True)
    cwe = models.TextField(max_length=20, blank=True, null=True)
    osvdb = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    KEY_FIELDS = ('technology', 'name', 'cve')


class Credential(Finding):
    email = models.TextField(max_length=100, blank=True, null=True)
    username = models.TextField(max_length=100, blank=True, null=True)
    secret = models.TextField(max_length=300, blank=True, null=True)

    KEY_FIELDS = ('email', 'username', 'secret')


class Exploit(Finding):
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

    KEY_FIELDS = ('technology', 'vulnerability', 'name', 'reference')

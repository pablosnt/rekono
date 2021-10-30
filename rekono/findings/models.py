from typing import Any, Collection, Iterable, Optional

from django.core.exceptions import ValidationError
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

    key_fields = ['execution__task']

    class Meta:
        abstract = True

    def validate_unique(self, exclude: Optional[Collection[str]] = ...) -> None:
        if not self.execution:
            return
        filter = {}
        for field in self.key_fields:
            filter[field] = self.get_field(field)
        if self._meta.model.objects.filter(**filter).exists():
            raise ValidationError('Unique constraint violation')

    def save(self, *args, **kwargs):
        self.validate_unique()
        return super().save(*args, **kwargs)

    def __hash__(self) -> int:
        hash_fields = []
        for field in self.key_fields:
            hash_fields.append(self.get_field(field))
        return hash(tuple(hash_fields))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            equals = True
            for field in self.key_fields:
                equals = equals and (self.get_field(field) == o.get_field(field))

    def get_field(self, field: str) -> str:
        relations = field.split('__') if '__' in field else [field]
        value = self
        for relation in relations:
            value = getattr(value, relation)
            if not value:
                break
        return value

    def get_project(self) -> Any:
        return self.execution.task.target.project


class OSINT(Finding):
    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=DataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = ['execution__task', 'data', 'data_type']


class Host(Finding):
    address = models.TextField(max_length=20)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.TextField(max_length=10, choices=OSType.choices, default=OSType.OTHER)

    key_fields = ['execution__task', 'address']


class Enumeration(Finding):
    host = models.ForeignKey(
        Host,
        related_name='enumeration',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    port = models.IntegerField()
    port_status = models.TextField(
        max_length=15,
        choices=PortStatus.choices,
        default=PortStatus.OPEN
    )
    protocol = models.TextField(max_length=5, choices=Protocol.choices, blank=True, null=True)
    service = models.TextField(max_length=50, blank=True, null=True)

    key_fields = ['execution__task', 'host', 'port']


class Endpoint(Finding):
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='endpoint',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    endpoint = models.TextField(max_length=500)
    status = models.IntegerField(blank=True, null=True)

    key_fields = ['execution__task', 'enumeration', 'endpoint']


class Technology(Finding):
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='technology',
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

    key_fields = ['execution__task', 'enumeration', 'name', 'version']


class Vulnerability(Finding):
    technology = models.ForeignKey(
        Technology,
        related_name='vulnerability',
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

    key_fields = ['execution__task', 'technology', 'name', 'description', 'cve']


class Credential(Finding):
    email = models.TextField(max_length=100, blank=True, null=True)
    username = models.TextField(max_length=100, blank=True, null=True)
    secret = models.TextField(max_length=300, blank=True, null=True)

    key_fields = ['execution__task', 'email', 'username', 'secret']


class Exploit(Finding):
    vulnerability = models.ForeignKey(
        Vulnerability,
        related_name='exploit',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    technology = models.ForeignKey(
        Technology,
        related_name='exploit',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    checked = models.BooleanField(default=False)

    key_fields = ['execution__task', 'technology', 'vulnerability', 'name', 'reference']

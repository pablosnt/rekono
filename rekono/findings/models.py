from typing import Any, Collection, Dict, Iterable, Optional, Tuple

from defectdojo.api.constants import DD_FINDING_DATE_FORMAT
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS, models
from executions.models import Execution
from findings.enums import DataType, OSType, PortStatus, Protocol, Severity
from findings.utils import get_unique_filter
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from input_types.utils import get_url
from targets.enums import TargetType
from targets.utils import get_target_type
from tools.models import Input

# Create your models here.


def create_finding_foreign_key(model, name):
    return models.ForeignKey(
        model,
        related_name=name,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )


class Finding(models.Model, BaseInput):
    execution = models.ForeignKey(Execution, related_name='%(class)s', on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    reported_to_defectdojo = models.BooleanField(default=False)

    key_fields = []

    class Meta:
        abstract = True
        ordering = ['-id']

    def validate_unique(self, exclude: Optional[Collection[str]] = None) -> None:
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.execution)
        search = self._meta.model.objects.filter(**unique_filter)
        if search.exists():
            raise ValidationError('Unique constraint violation')
 
    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = DEFAULT_DB_ALIAS,
        update_fields: Optional[Iterable[str]] = None
    ) -> None:
        if not self.id:
            self.validate_unique()
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __hash__(self) -> int:
        hash_fields = []
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.execution)
        for value in unique_filter.values():
            hash_fields.append(value)
        return hash(tuple(hash_fields))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            equals = True
            unique_filter = get_unique_filter(o.key_fields, vars(o), o.execution)
            for key, value in get_unique_filter(self.key_fields, vars(self), self.execution).items():
                equals = equals and (unique_filter[key] == value)
            return equals
        return False

    def get_project(self) -> Any:
        return self.execution.task.target.project


class OSINT(Finding):
    data = models.TextField(max_length=250)
    data_type = models.TextField(max_length=10, choices=DataType.choices)
    source = models.TextField(max_length=50, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = [
        {'name': 'data', 'is_base': False},
        {'name': 'data_type', 'is_base': False}
    ]

    def parse(self, accumulated: dict = {}) -> dict:
        if self.data_type in [DataType.IP, DataType.DOMAIN]:
            return {
                InputKeyword.TARGET.name.lower(): self.data,
                InputKeyword.HOST.name.lower(): self.data,
                InputKeyword.URL.name.lower(): get_url(self.data)
            }
        return {}

    def defect_dojo(self):
        return {
            'title': f'{self.data_type} found using OSINT techniques',
            'description': self.data,
            'severity': Severity.MEDIUM.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Host(Finding):
    address = models.TextField(max_length=30)
    os = models.TextField(max_length=250, blank=True, null=True)
    os_type = models.TextField(max_length=10, choices=OSType.choices, default=OSType.OTHER)

    key_fields = [
        {'name': 'address', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        if not input.filter:
            return True
        try:
            return TargetType[input.filter] == get_target_type(self.address)
        except KeyError:
            return True

    def parse(self, accumulated: dict = {}) -> dict:
        return {
            InputKeyword.TARGET.name.lower(): self.address,
            InputKeyword.HOST.name.lower(): self.address,
            InputKeyword.URL.name.lower(): get_url(self.address),
        }

    def defect_dojo(self):
        description = self.address
        if self.os:
            description += '- {self.os} ({self.os_type})'
        return {
            'title': 'Host discovered',
            'description': description,
            'severity': Severity.INFO.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Enumeration(Finding):
    host = create_finding_foreign_key(Host, 'enumeration')
    port = models.IntegerField()
    port_status = models.TextField(
        max_length=15,
        choices=PortStatus.choices,
        default=PortStatus.OPEN
    )
    protocol = models.TextField(max_length=5, choices=Protocol.choices, blank=True, null=True)
    service = models.TextField(max_length=50, blank=True, null=True)

    key_fields = [
        {'name': 'host_id', 'is_base': True},
        {'name': 'port', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        if not input.filter:
            return True
        try:
            to_check = int(input.filter)
            return to_check == self.port
        except ValueError:
            return input.filter in self.service

    def parse(self, accumulated: dict = {}) -> dict:
        output = {
            InputKeyword.TARGET.name.lower(): f'{self.host.address}:{self.port}',
            InputKeyword.HOST.name.lower(): self.host.address,
            InputKeyword.PORT.name.lower(): self.port,
            InputKeyword.PORTS.name.lower(): [self.port],
            InputKeyword.URL.name.lower(): get_url(self.host.address, self.port),
        }
        if accumulated and InputKeyword.PORTS.name.lower() in accumulated:
            output[InputKeyword.PORTS.name.lower()] = accumulated[InputKeyword.PORTS.name.lower()]
            output[InputKeyword.PORTS.name.lower()].append(self.port)
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ','.join([str(port) for port in output[InputKeyword.PORTS.name.lower()]])    # noqa: E501
        return output

    def defect_dojo(self):
        description = f'{self.port} - {self.port_status} - {self.protocol} - {self.service}'
        return {
            'title': 'Port discovered',
            'description': description,
            'severity': Severity.INFO.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Endpoint(Finding):
    enumeration = create_finding_foreign_key(Enumeration, 'endpoint')
    endpoint = models.TextField(max_length=500)
    status = models.IntegerField(blank=True, null=True)

    key_fields = [
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'endpoint', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        if not input.filter:
            return True
        try:
            status_code = int(input.filter)
            return status_code == self.status
        except ValueError:
            return self.endpoint.startswith(input.filter)

    def parse(self, accumulated: dict = {}) -> dict:
        output = self.enumeration.parse()
        output[InputKeyword.URL.name.lower()] = get_url(
            self.enumeration.host.address,
            self.enumeration.port,
            self.endpoint
        )
        output[InputKeyword.ENDPOINT.name.lower()] = self.endpoint
        return output

    def defect_dojo(self):
        return {
            'protocol': self.enumeration.service,
            'host': self.enumeration.host.address,
            'port': self.enumeration.port,
            'path': self.endpoint
        }


class Technology(Finding):
    enumeration = create_finding_foreign_key(Enumeration, 'technology')
    name = models.TextField(max_length=100)
    version = models.TextField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    related_to = create_finding_foreign_key('Technology', 'related_technologies')
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = [
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'name', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        return not input.filter or input.filter.lower() in self.name.lower()

    def parse(self, accumulated: dict = {}) -> dict:
        output = self.enumeration.parse()
        output[InputKeyword.TECHNOLOGY.name.lower()] = self.name
        if self.version:
            output[InputKeyword.VERSION.name.lower()] = self.version
        return output

    def defect_dojo(self):
        return {
            'title': f'Technology {self.name} detected',
            'description': self.description if self.description else f'{self.name} {self.version}',
            'severity': Severity.LOW.value,
            'cwe': 200,     # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            'references': self.reference,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Vulnerability(Finding):
    technology = create_finding_foreign_key(Technology, 'vulnerability')
    enumeration = create_finding_foreign_key(Enumeration, 'vulnerability')
    name = models.TextField(max_length=50)
    description = models.TextField(blank=True, null=True)
    severity = models.TextField(choices=Severity.choices, default=Severity.MEDIUM)
    cve = models.TextField(max_length=20, blank=True, null=True)
    cwe = models.TextField(max_length=20, blank=True, null=True)
    osvdb = models.TextField(max_length=20, blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)

    key_fields = [
        {'name': 'technology_id', 'is_base': True},
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'cve', 'is_base': False},
        {'name': 'name', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        if not input.filter:
            return True
        try:
            return Severity[input.filter] == self.severity
        except ValueError:
            f = input.filter.lower()
            return (
                f == 'cve' and self.cve
                or (f.startswith('cve-') and f == self.cve.lower())
                or (f.startswith('cwe-') and f == self.cwe.lower())
            )
    
    def parse(self, accumulated: dict = {}) -> dict:
        output = {}
        if self.enumeration:
            output = self.enumeration.parse()
        elif self.technology:
            output = self.technology.parse()
        if self.cve:
            output[InputKeyword.CVE.name.lower()] = self.cve
        return output

    def defect_dojo(self):
        return {
            'title': self.name,
            'description': self.description,
            'severity': Severity(self.severity).value,
            'cve': self.cve,
            'cwe': int(self.cwe.split('-', 1)[1]) if self.cwe else None,
            'references': self.reference,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Credential(Finding):
    email = models.TextField(max_length=100, blank=True, null=True)
    username = models.TextField(max_length=100, blank=True, null=True)
    secret = models.TextField(max_length=300, blank=True, null=True)

    key_fields = [
        {'name': 'email', 'is_base': False},
        {'name': 'username', 'is_base': False},
        {'name': 'secret', 'is_base': False}
    ]

    def parse(self, accumulated: dict = ...) -> dict:
        return {
            InputKeyword.EMAIL.name.lower(): self.email,
            InputKeyword.USERNAME.name.lower(): self.username,
            InputKeyword.SECRET.name.lower(): self.secret,
        }

    def defect_dojo(self):
        description = ' - '.join([getattr(self, f) for f in ['email', 'username', 'secret']])
        return {
            'title': 'Credentials exposure',
            'description': description,
            'cwe': 200,     # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            'severity': Severity.HIGH.value,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }


class Exploit(Finding):
    vulnerability = create_finding_foreign_key(Vulnerability, 'exploit')
    technology = create_finding_foreign_key(Technology, 'exploit')
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reference = models.TextField(max_length=250, blank=True, null=True)
    checked = models.BooleanField(default=False)

    key_fields = [
        {'name': 'vulnerability_id', 'is_base': True},
        {'name': 'technology_id', 'is_base': True},
        {'name': 'name', 'is_base': False},
        {'name': 'reference', 'is_base': False}
    ]

    def parse(self, accumulated: dict = {}) -> dict:
        output = self.vulnerability.parse()
        output[InputKeyword.EXPLOIT.name.lower()] = self.name
        return output

    def defect_dojo(self):
        return {
            'title': f'Exploit {self.name} found',
            'description': self.description,
            'severity': Severity(self.vulnerability.severity).value if self.vulnerability else Severity.MEDIUM.value,   # noqa: E501
            'reference': self.reference,
            'date': self.creation.strftime(DD_FINDING_DATE_FORMAT)
        }

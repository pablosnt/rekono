from typing import Any, Dict, List, Union, cast

from defectdojo.constants import DD_DATE_FORMAT
from django.db import models
from executions.models import Execution
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from input_types.utils import get_url
from projects.models import Project
from targets.enums import TargetType
from targets.utils import get_target_type
from tools.models import Input, Tool

from findings.enums import (DataType, OSType, PathType, PortStatus, Protocol,
                            Severity)
from findings.utils import get_unique_filter

# Create your models here.


def create_finding_foreign_key(model: Union[models.Model, str], name: str) -> models.ForeignKey:
    '''Create a foreign key field to create a relationship between two Finding models.

    Args:
        model (Union[models.Model, str]): Finding model of the foreign key
        name (str): Related name of the foreign key

    Returns:
        models.ForeignKey: Foreign key field
    '''
    return models.ForeignKey(model, related_name=name, on_delete=models.DO_NOTHING, blank=True, null=True)


class Finding(models.Model, BaseInput):
    '''Common and abstract Finding model, to define the common fields for all Finding models.'''

    # Execution where the finding is found
    executions = models.ManyToManyField(Execution, related_name='%(class)s')
    detected_by = models.ForeignKey(Tool, on_delete=models.SET_NULL, blank=True, null=True)
    first_seen = models.DateTimeField(auto_now_add=True)                        # First date when the finding appear
    last_seen = models.DateTimeField(auto_now_add=True)                         # Last date when the finding appear
    is_active = models.BooleanField(default=True)                               # Indicate if the finding is active

    key_fields: List[Dict[str, Any]] = []                                       # Unique field list

    class Meta:
        '''Model metadata.'''

        abstract = True                                                         # To be extended by Finding models

    def __hash__(self) -> int:
        '''Get an unique value based on the object unique fields.

        Returns:
            int: Calculated unique value
        '''
        hash_fields = []
        # Get unique filter from key fields
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.executions.first().task.target)
        for value in unique_filter.values():
            hash_fields.append(value)                                           # Add values to the calculation
        return hash(tuple(hash_fields))                                         # Hash calculation

    def __eq__(self, o: object) -> bool:
        '''Check if other object is equals to this object.

        Args:
            o (object): Other object to compare

        Returns:
            bool: Indicate if both objects are equal or not
        '''
        if isinstance(o, self.__class__):                                       # Check object class
            equals = True
            # Get object unique filter from object key fields
            other_filter = get_unique_filter(o.key_fields, vars(o), o.executions.first().task.target)
            self_filter = get_unique_filter(self.key_fields, vars(self), self.executions.first().task.target)
            # Get unique filter from key fields
            for key, value in self_filter.items():
                equals = equals and (other_filter.get(key) == value)            # Compare all key fields
            return equals
        return False

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.executions.first().task.target.project


class OSINT(Finding):
    '''OSINT model.'''

    data = models.TextField(max_length=250)                                     # OSINT data found
    data_type = models.TextField(max_length=10, choices=DataType.choices)       # OSINT data type
    source = models.TextField(max_length=50, blank=True, null=True)             # Source where data has been found
    reference = models.TextField(max_length=250, blank=True, null=True)         # Reference associated to the data

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'data', 'is_base': False},
        {'name': 'data_type', 'is_base': False}
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        if self.data_type in [DataType.IP, DataType.DOMAIN]:
            return {
                InputKeyword.TARGET.name.lower(): self.data,
                InputKeyword.HOST.name.lower(): self.data,
                InputKeyword.URL.name.lower(): get_url(self.data)
            }
        return {}

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'title': f'{self.data_type} found using OSINT techniques',
            'description': self.data,
            'severity': str(Severity.MEDIUM),
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.data


class Host(Finding):
    '''Host model.'''

    address = models.TextField(max_length=30)                                   # Host address
    os = models.TextField(max_length=250, blank=True, null=True)                # OS full specification
    os_type = models.TextField(max_length=10, choices=OSType.choices, default=OSType.OTHER)         # OS categorization

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'address', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            distinct = input.filter[0] == '!'
            filter_types = [
                cast(models.TextChoices, TargetType)[f.upper()] for f in input.filter.replace('!', '').split(',s')
            ]
            host_type = get_target_type(self.address)
            return host_type not in filter_types if distinct else host_type in filter_types
        except KeyError:
            return True

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        return {
            InputKeyword.TARGET.name.lower(): self.address,
            InputKeyword.HOST.name.lower(): self.address,
            InputKeyword.URL.name.lower(): get_url(self.address),
        }

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        description = self.address
        if self.os:
            description += '- {self.os} ({self.os_type})'
        return {
            'title': 'Host discovered',
            'description': description,
            'severity': str(Severity.INFO),
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.address


class Port(Finding):
    '''Port model.'''

    host = create_finding_foreign_key(Host, 'port')                             # Host where the port is discovered
    port = models.IntegerField()                                                # Port number
    status = models.TextField(max_length=15, choices=PortStatus.choices, default=PortStatus.OPEN)   # Port status
    protocol = models.TextField(max_length=5, choices=Protocol.choices, blank=True, null=True)      # Transport protocol
    service = models.TextField(max_length=50, blank=True, null=True)            # Service protocol if found

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'host_id', 'is_base': True},
        {'name': 'port', 'is_base': False},
        {'name': 'protocol', 'is_base': False},
    ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            to_check = int(input.filter)
            # If the filter is a number, will be filtered by port
            return to_check == self.port
        except ValueError:
            # If the filter is a string, will be filtered by service
            return input.filter.lower() in self.service.lower()

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
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
        output[InputKeyword.PORTS_COMMAS.name.lower()] = ','.join([str(p) for p in output[InputKeyword.PORTS.name.lower()]])    # noqa: E501
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        description = f'{self.port} - {self.status} - {self.protocol} - {self.service}'
        if self.host:
            description = f'{self.host.address} - {description}'
        return {
            'title': 'Port discovered',
            'description': description,
            'severity': str(Severity.INFO),
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.host.__str__()} - {self.port}' if self.host else str(self.port)


class Path(Finding):
    '''Path model.'''

    port = create_finding_foreign_key(Port, 'path')                             # Port where path is discovered
    path = models.TextField(max_length=500)                                     # Path value
    # Status receive for that path. Probably HTTP status
    status = models.IntegerField(blank=True, null=True)
    extra = models.TextField(max_length=100, blank=True, null=True)             # Extra information related to the path
    # Path type depending on the protocol where it's found
    type = models.TextField(choices=PathType.choices, default=PathType.ENDPOINT)

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'port_id', 'is_base': True},
        {'name': 'path', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            # If filter is a valid severity, vulnerability will be filtered by severity
            return cast(models.TextChoices, PathType)[input.filter.upper()] == self.type
        except KeyError:
            try:
                status_code = int(input.filter)
                # If the filter is a number, will be filtered by status
                return status_code == self.status
            except ValueError:
                # If the filter is a string, will be filtered by path
                return input.filter in self.path

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.port.parse() if self.port else {}
        if self.type == PathType.ENDPOINT:
            output[InputKeyword.URL.name.lower()] = get_url(
                self.port.host.address,
                self.port.port,
                self.path
            )
        output[InputKeyword.ENDPOINT.name.lower()] = self.path
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'protocol': self.port.service if self.port else None,
            'host': self.port.host.address if self.port else None,
            'port': self.port.port if self.port else None,
            'path': self.path
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.port.__str__()} - {self.path}' if self.port else self.path


class Technology(Finding):
    '''Technology model.'''

    port = create_finding_foreign_key(Port, 'technology')                       # Port where technology is discovered
    name = models.TextField(max_length=100)                                     # Technology name
    version = models.TextField(max_length=100, blank=True, null=True)           # Technology version
    description = models.TextField(max_length=200, blank=True, null=True)       # Technology description
    related_to = create_finding_foreign_key('Technology', 'related_technologies')   # Related technology if exists
    reference = models.TextField(max_length=250, blank=True, null=True)         # Technology reference

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'port_id', 'is_base': True},
        {'name': 'name', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        return not input.filter or input.filter.lower() in self.name.lower()    # Filter by technology name

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.port.parse() if self.port else {}
        output[InputKeyword.TECHNOLOGY.name.lower()] = self.name
        if self.version:
            output[InputKeyword.VERSION.name.lower()] = self.version
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'title': f'Technology {self.name} detected',
            'description': self.description if self.description else f'{self.name} {self.version}',
            'severity': str(Severity.LOW),
            'cwe': 200,     # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            'references': self.reference,
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.port.__str__()} - {self.name}' if self.port else self.name


class Credential(Finding):
    '''Credential model.'''

    # Technology where credentials are discovered
    technology = create_finding_foreign_key(Technology, 'technology')
    email = models.TextField(max_length=100, blank=True, null=True)             # Email if found
    username = models.TextField(max_length=100, blank=True, null=True)          # Username if found
    secret = models.TextField(max_length=300, blank=True, null=True)            # Secret (password, key, etc.) if found
    context = models.TextField(max_length=300, blank=True, null=True)           # Context information about credential

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'email', 'is_base': False},
        {'name': 'username', 'is_base': False},
        {'name': 'secret', 'is_base': False}
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        return {
            InputKeyword.EMAIL.name.lower(): self.email,
            InputKeyword.USERNAME.name.lower(): self.username,
            InputKeyword.SECRET.name.lower(): self.secret,
        }

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        description = ' - '.join([getattr(self, f) for f in ['email', 'username', 'secret']])
        return {
            'title': 'Credentials exposure',
            'description': description,
            'cwe': 200,     # CWE-200: Exposure of Sensitive Information to Unauthorized Actor
            'severity': str(Severity.HIGH),
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        text = f'{self.email} - {self.username} - {self.secret}'
        if self.technology:
            text = f'{self.technology.__str__()} - {text}'
        return text


class Vulnerability(Finding):
    '''Vulnerability model.'''

    # Technology where vulnerability is found
    technology = create_finding_foreign_key(Technology, 'vulnerability')
    # Port where vulnerability is found. Only if technology is null
    port = create_finding_foreign_key(Port, 'vulnerability')
    name = models.TextField(max_length=50)                                      # Vulnerability name
    description = models.TextField(blank=True, null=True)                       # Vulnerability description
    severity = models.TextField(choices=Severity.choices, default=Severity.MEDIUM)  # Vulnerability severity
    cve = models.TextField(max_length=20, blank=True, null=True)                # CVE
    cwe = models.TextField(max_length=20, blank=True, null=True)                # CWE
    osvdb = models.TextField(max_length=20, blank=True, null=True)              # OSVDB
    reference = models.TextField(max_length=250, blank=True, null=True)         # Vulnerability reference

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'technology_id', 'is_base': True},
        {'name': 'port_id', 'is_base': True},
        {'name': 'cve', 'is_base': False},
        {'name': 'name', 'is_base': False}
    ]

    def filter(self, input: Input) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Input): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        if not input.filter:
            return True
        try:
            # If filter is a valid severity, vulnerability will be filtered by severity
            return cast(models.TextChoices, Severity)[input.filter.upper()] == self.severity
        except KeyError:
            f = input.filter.lower()
            # If filter is a string, vulnerability will be filtered by:
            return (
                (self.cve and (f == 'cve' or (f.startswith('cve-') and f == self.cve.lower()))) or  # CVE
                (self.cwe and (f.startswith('cwe-') and f == self.cwe.lower()))                     # CWE
            )

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = {}
        if self.technology:
            output = self.technology.parse()
        elif self.port:
            output = self.port.parse()
        if self.cve:
            output[InputKeyword.CVE.name.lower()] = self.cve
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'title': self.name,
            'description': self.description,
            'severity': Severity(self.severity).value,
            'cve': self.cve,
            'cwe': int(self.cwe.split('-', 1)[1]) if self.cwe else None,
            'references': self.reference,
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        text = self.name
        if self.technology:
            text = f'{self.technology.__str__()} - {self.name}'
        elif self.port:
            text = f'{self.port.__str__()} - {self.name}'
        if self.cve:
            text = f'{text} - {self.cve}'
        return text


class Exploit(Finding):
    '''Exploit model.'''

    vulnerability = create_finding_foreign_key(Vulnerability, 'exploit')        # Vulnerability that the exploit abuses
    # Technology that the exploit abuses.  Only if vulnerability is null
    technology = create_finding_foreign_key(Technology, 'exploit')
    title = models.TextField(max_length=100)                                    # Exploit title
    edb_id = models.IntegerField(blank=True, null=True)                         # Id in Exploit-DB
    reference = models.TextField(max_length=250, blank=True, null=True)         # Exploit reference

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'vulnerability_id', 'is_base': True},
        {'name': 'technology_id', 'is_base': True},
        {'name': 'reference', 'is_base': False}
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = {}
        if self.vulnerability:
            output = self.vulnerability.parse()
        elif self.technology:
            output = self.technology.parse()
        output[InputKeyword.EXPLOIT.name.lower()] = self.title
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'title': f'Exploit {self.edb_id} found' if self.edb_id else 'Exploit found',
            'description': self.title,
            'severity': Severity(self.vulnerability.severity).value if self.vulnerability else str(Severity.MEDIUM),
            'reference': self.reference,
            'date': self.last_seen.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        text = self.title
        if self.vulnerability:
            text = f'{self.vulnerability.__str__()} - {self.title}'
        elif self.technology:
            text = f'{self.technology.__str__()} - {self.title}'
        return text

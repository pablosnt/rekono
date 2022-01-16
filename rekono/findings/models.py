from typing import Any, Collection, Dict, Iterable, List, Optional, Union, cast

from defectdojo.constants import DD_DATE_FORMAT
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS, models
from executions.models import Execution
from findings.enums import DataType, OSType, PortStatus, Protocol, Severity
from findings.utils import get_unique_filter
from input_types.base import BaseInput
from input_types.enums import InputKeyword
from input_types.utils import get_url
from projects.models import Project
from targets.enums import TargetType
from targets.utils import get_target_type
from tools.models import Input

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
    execution = models.ForeignKey(Execution, related_name='%(class)s', on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)                          # Creation date of the finding
    is_active = models.BooleanField(default=True)                               # Indicate if the finding is active
    # Indicate if the finding has been imported in Defect-Dojo
    reported_to_defectdojo = models.BooleanField(default=False)

    key_fields: List[Dict[str, Any]] = []                                       # Unique field list

    class Meta:
        '''Model metadata.'''

        abstract = True                                                         # To be extended by Finding models
        ordering = ['-id']                                                      # Default ordering for pagination

    def validate_unique(self, exclude: Optional[Collection[str]] = None) -> None:
        '''Validate all uniqueness constraints on the model.

        Args:
            exclude (Optional[Collection[str]], optional): Field names to be exclude from validation. Defaults to None

        Raises:
            ValidationError: Raised if one unique constraint is violated
        '''
        # Get unique filter from key fields
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.execution)
        search = self._meta.model.objects.filter(**unique_filter)               # Filter findings with the unique filter
        if search.exists():                                                     # If findings found
            raise ValidationError('Unique constraint violation')                # Unique constraint violation

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = DEFAULT_DB_ALIAS,
        update_fields: Optional[Iterable[str]] = None
    ) -> None:
        '''Save object in database.

        Args:
            force_insert (bool, optional): Force an INSERT query. Defaults to False
            force_update (bool, optional): Force an UPDATE query. Defaults to False
            using (Optional[str], optional): Database alias. Defaults to DEFAULT_DB_ALIAS
            update_fields (Optional[Iterable[str]], optional): Fields to be saved. Defaults to None
        '''
        # If Id is not setted, it's an insertion. If Id is setted, it's an update
        if not self.id:
            self.validate_unique()                                              # Check constraint only in insertions
        super().save(                                                           # Call parent save method
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __hash__(self) -> int:
        '''Get an unique value based on the object unique fields.

        Returns:
            int: Calculated unique value
        '''
        hash_fields = []
        # Get unique filter from key fields
        unique_filter = get_unique_filter(self.key_fields, vars(self), self.execution)
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
            unique_filter = get_unique_filter(o.key_fields, vars(o), o.execution)
            # Get unique filter from key fields
            for key, value in get_unique_filter(self.key_fields, vars(self), self.execution).items():
                equals = equals and (unique_filter[key] == value)               # Compare all key fields
            return equals
        return False

    def get_project(self) -> Project:
        '''Get the related project for the instance. This will be used for authorization purposes.

        Returns:
            Project: Related project entity
        '''
        return self.execution.task.target.project


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
            'date': self.creation.strftime(DD_DATE_FORMAT)
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
            # Filter by address type
            return cast(models.TextChoices, TargetType)[input.filter] == get_target_type(self.address)
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
            'date': self.creation.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.address


class Enumeration(Finding):
    '''Enumeration model.'''

    host = create_finding_foreign_key(Host, 'enumeration')                      # Host where the port is discovered
    port = models.IntegerField()                                                # Port number
    port_status = models.TextField(max_length=15, choices=PortStatus.choices, default=PortStatus.OPEN)  # Port status
    protocol = models.TextField(max_length=5, choices=Protocol.choices, blank=True, null=True)      # Transport protocol
    service = models.TextField(max_length=50, blank=True, null=True)            # Service protocol if found

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'host_id', 'is_base': True},
        {'name': 'port', 'is_base': False}
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
            # If the filter is a number, enumeration will be filtered by port
            return to_check == self.port
        except ValueError:
            # If the filter is a string, enumeration will be filtered by service
            return input.filter in self.service

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
        description = f'{self.port} - {self.port_status} - {self.protocol} - {self.service}'
        if self.host:
            description = f'{self.host.address} - {description}'
        return {
            'title': 'Port discovered',
            'description': description,
            'severity': str(Severity.INFO),
            'date': self.creation.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.host.__str__()} - {self.port}' if self.host else str(self.port)


class Endpoint(Finding):
    '''Endpoint model.'''

    enumeration = create_finding_foreign_key(Enumeration, 'endpoint')           # Port where endpoint is discovered
    endpoint = models.TextField(max_length=500)                                 # Endpoint value
    # Status receive for that endpoint. Probably HTTP status
    status = models.IntegerField(blank=True, null=True)

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'enumeration_id', 'is_base': True},
        {'name': 'endpoint', 'is_base': False}
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
            status_code = int(input.filter)
            # If the filter is a number, endpoint will be filtered by status
            return status_code == self.status
        except ValueError:
            # If the filter is a string, endpoint will be filtered by endpoint
            return self.endpoint.startswith(input.filter)

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.enumeration.parse() if self.enumeration else {}
        output[InputKeyword.URL.name.lower()] = get_url(
            self.enumeration.host.address,
            self.enumeration.port,
            self.endpoint
        )
        output[InputKeyword.ENDPOINT.name.lower()] = self.endpoint
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'protocol': self.enumeration.service,
            'host': self.enumeration.host.address,
            'port': self.enumeration.port,
            'path': self.endpoint
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.enumeration.__str__()} - {self.endpoint}' if self.enumeration else self.endpoint


class Technology(Finding):
    '''Technology model.'''

    enumeration = create_finding_foreign_key(Enumeration, 'technology')         # Port where technology is discovered
    name = models.TextField(max_length=100)                                     # Technology name
    version = models.TextField(max_length=100, blank=True, null=True)           # Technology version
    description = models.TextField(max_length=200, blank=True, null=True)       # Technology description
    related_to = create_finding_foreign_key('Technology', 'related_technologies')   # Related technology if exists
    reference = models.TextField(max_length=250, blank=True, null=True)         # Technology reference

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'enumeration_id', 'is_base': True},
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
        output = self.enumeration.parse() if self.enumeration else {}
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
            'date': self.creation.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.enumeration.__str__()} - {self.name}' if self.enumeration else self.name


class Vulnerability(Finding):
    '''Vulnerability model.'''

    # Technology where vulnerability is found
    technology = create_finding_foreign_key(Technology, 'vulnerability')
    # Port where vulnerability is found. Only if technology is null
    enumeration = create_finding_foreign_key(Enumeration, 'vulnerability')
    name = models.TextField(max_length=50)                                      # Vulnerability name
    description = models.TextField(blank=True, null=True)                       # Vulnerability description
    severity = models.TextField(choices=Severity.choices, default=Severity.MEDIUM)  # Vulnerability severity
    cve = models.TextField(max_length=20, blank=True, null=True)                # CVE
    cwe = models.TextField(max_length=20, blank=True, null=True)                # CWE
    osvdb = models.TextField(max_length=20, blank=True, null=True)              # OSVDB
    reference = models.TextField(max_length=250, blank=True, null=True)         # Vulnerability reference

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'technology_id', 'is_base': True},
        {'name': 'enumeration_id', 'is_base': True},
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
            return cast(models.TextChoices, Severity)[input.filter] == self.severity
        except ValueError:
            f = input.filter.lower()
            # If filter is a string, vulnerability will be filtered by:
            return (
                f == 'cve' and self.cve or                                      # CVE found or not
                (f.startswith('cve-') and f == self.cve.lower()) or             # Specific CVE
                (f.startswith('cwe-') and f == self.cwe.lower())                # Specific CWE
            )

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.technology.parse() if self.technology else self.enumeration.parse() if self.enumeration else {}
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
            'date': self.creation.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        text = self.name
        if self.technology:
            text = f'{self.technology.__str__()} - {self.name}'
        elif self.enumeration:
            text = f'{self.enumeration.__str__()} - {self.name}'
        if self.cve:
            text = f'{text} - {self.cve}'
        return text


class Credential(Finding):
    '''Credential model.'''

    email = models.TextField(max_length=100, blank=True, null=True)             # Email if found
    username = models.TextField(max_length=100, blank=True, null=True)          # Username if found
    secret = models.TextField(max_length=300, blank=True, null=True)            # Secret (password, key, etc.) if found

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
            'date': self.creation.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return f'{self.email} - {self.username} - {self.secret}'


class Exploit(Finding):
    '''Exploit model.'''

    vulnerability = create_finding_foreign_key(Vulnerability, 'exploit')        # Vulnerability that the exploit abuses
    # Technology that the exploit abuses.  Only if vulnerability is null
    technology = create_finding_foreign_key(Technology, 'exploit')
    name = models.TextField(max_length=100)                                     # Exploit name
    description = models.TextField(blank=True, null=True)                       # Exploit description
    reference = models.TextField(max_length=250, blank=True, null=True)         # Exploit reference
    checked = models.BooleanField(default=False)                                # Indicate if the exploit is confirmed

    key_fields: List[Dict[str, Any]] = [                                        # Unique field list
        {'name': 'vulnerability_id', 'is_base': True},
        {'name': 'technology_id', 'is_base': True},
        {'name': 'name', 'is_base': False},
        {'name': 'reference', 'is_base': False}
    ]

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        output = self.vulnerability.parse() if self.vulnerability else self.technology.parse() if self.technology else {}   # noqa: E501
        output[InputKeyword.EXPLOIT.name.lower()] = self.name
        return output

    def defect_dojo(self) -> Dict[str, Any]:
        '''Get useful information to import this finding in Defect-Dojo.

        Returns:
            Dict[str, Any]: Useful information for Defect-Dojo imports
        '''
        return {
            'title': f'Exploit {self.name} found',
            'description': self.description,
            'severity': Severity(self.vulnerability.severity).value if self.vulnerability else str(Severity.MEDIUM),
            'reference': self.reference,
            'date': self.creation.strftime(DD_DATE_FORMAT)
        }

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        text = self.name
        if self.vulnerability:
            text = f'{self.vulnerability.__str__()} - {self.name}'
        elif self.technology:
            text = f'{self.technology.__str__()} - {self.name}'
        return text

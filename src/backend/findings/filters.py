from typing import List

from api.filters import BaseToolFilter
from django.db.models import QuerySet
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter

from findings.enums import OSType
from findings.models import (OSINT, Credential, Exploit, Host, Path, Port,
                             Technology, Vulnerability)

# Common ordering anf filtering fields for all Finding models
FINDING_ORDERING = (
    ('executions__task', 'task'),
    ('executions__task__target', 'target'),
    ('executions__task__target__project', 'project'),
    ('executions__task__executor', 'executor'),
    'executions',
    'detected_by',
    'first_seen',
    'last_seen',
    'is_active'
)
FINDING_FILTERING = {
    'executions': ['exact'],
    'executions__task': ['exact'],
    'executions__task__target': ['exact'],
    'executions__task__target__target': ['exact', 'icontains'],
    'executions__task__target__project': ['exact'],
    'executions__task__target__project__name': ['exact', 'icontains'],
    'executions__task__executor': ['exact'],
    'executions__task__executor__username': ['exact', 'icontains'],
    'executions__start': ['gte', 'lte', 'exact'],
    'executions__end': ['gte', 'lte', 'exact'],
    'detected_by': ['exact'],
    'detected_by__name': ['exact', 'icontains'],
    'first_seen': ['gte', 'lte', 'exact'],
    'last_seen': ['gte', 'lte', 'exact'],
    'is_active': ['exact'],
}


class FindingFilter(BaseToolFilter):
    '''Common FilterSet to filter and sort findings entities.'''

    tool_fields: List[str] = ['executions__task__tool', 'executions__step__tool']   # Filter by two Tool fields


class BaseVulnerabilityFilter(FindingFilter):
    '''Common FilterSet to filter findings entities based on vulnerability fields.'''

    port = filters.NumberFilter(method='filter_port')                           # Filter by port
    port_number = filters.NumberFilter(method='filter_port_number')             # Filter by port number
    host = filters.NumberFilter(method='filter_host')                           # Filter by host
    host_address = filters.CharFilter(method='filter_host_address')             # Filter by host address
    host_os_type = filters.ChoiceFilter(method='filter_host_os_type', choices=OSType.choices)       # Filter by host OS
    # Port field names to use in the filters
    port_fields: List[str] = []
    host_fields: List[str] = []                                                 # Host field names to use in the filters

    def filter_port(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        '''Filter queryset by port Id.

        Args:
            queryset (QuerySet): Finding queryset to be filtered
            name (str): Field name, not used in this case
            value (int): Port Id

        Returns:
            QuerySet: Filtered queryset by port Id
        '''
        return self.multiple_field_filter(queryset, value, self.port_fields)

    def filter_port_number(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        '''Filter queryset by port number.

        Args:
            queryset (QuerySet): Finding queryset to be filtered
            name (str): Field name, not used in this case
            value (int): Port number

        Returns:
            QuerySet: Filtered queryset by port number
        '''
        return self.multiple_field_filter(queryset, value, [f'{f}__port' for f in self.port_fields])

    def filter_host(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        '''Filter queryset by host Id.

        Args:
            queryset (QuerySet): Finding queryset to be filtered
            name (str): Field name, not used in this case
            value (int): Host Id

        Returns:
            QuerySet: Filtered queryset by host Id
        '''
        return self.multiple_field_filter(queryset, value, self.host_fields)

    def filter_host_address(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        '''Filter queryset by host address.

        Args:
            queryset (QuerySet): Finding queryset to be filtered
            name (str): Field name, not used in this case
            value (str): Host address

        Returns:
            QuerySet: Filtered queryset by host address
        '''
        return self.multiple_field_filter(queryset, value, [f'{f}__address' for f in self.host_fields])

    def filter_host_os_type(self, queryset: QuerySet, name: str, value: OSType) -> QuerySet:
        '''Filter queryset by host OS type.

        Args:
            queryset (QuerySet): Finding queryset to be filtered
            name (str): Field name, not used in this case
            value (OSType): OS type

        Returns:
            QuerySet: Filtered queryset by host OS type
        '''
        return self.multiple_field_filter(queryset, value, [f'{f}__os_type' for f in self.host_fields])


class OSINTFilter(FindingFilter):
    '''FilterSet to filter and sort OSINT entities.'''

    # Ordering fields including common ones
    o = OrderingFilter(fields=FINDING_ORDERING + ('data', 'data_type', 'source'))

    class Meta:
        '''FilterSet metadata.'''

        model = OSINT
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'data': ['exact', 'icontains'],
            'data_type': ['exact'],
            'source': ['exact', 'icontains'],
        })


class HostFilter(FindingFilter):
    '''FilterSet to filter and sort Host entities.'''

    o = OrderingFilter(fields=FINDING_ORDERING + ('address', 'os_type'))        # Ordering fields including common ones

    class Meta:
        '''FilterSet metadata.'''

        model = Host
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'address': ['exact', 'icontains'],
            'os_type': ['exact'],
        })


class PortFilter(FindingFilter):
    '''FilterSet to filter and sort Port entities.'''

    # Ordering fields including common ones
    o = OrderingFilter(
        fields=FINDING_ORDERING + (('host__os_type', 'os_type'), 'host', 'port', 'protocol', 'service', 'status')
    )

    class Meta:
        '''FilterSet metadata.'''

        model = Port
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'host': ['exact', 'isnull'],
            'host__address': ['exact', 'icontains'],
            'host__os_type': ['exact'],
            'port': ['exact'],
            'status': ['iexact'],
            'protocol': ['iexact'],
            'service': ['exact', 'icontains'],
        })


class PathFilter(FindingFilter):
    '''FilterSet to filter and sort Path entities.'''

    # Ordering fields including common ones
    o = OrderingFilter(fields=FINDING_ORDERING + (('port__host', 'host'), 'port', 'path', 'status', 'type'))

    class Meta:
        '''FilterSet metadata.'''

        model = Path
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'port': ['exact', 'isnull'],
            'port__host': ['exact'],
            'port__host__address': ['exact', 'icontains'],
            'port__host__os_type': ['exact'],
            'port__port': ['exact'],
            'path': ['exact', 'icontains'],
            'status': ['exact'],
            'type': ['exact'],
        })


class TechnologyFilter(FindingFilter):
    '''FilterSet to filter and sort Technology entities.'''

    # Ordering fields including common ones
    o = OrderingFilter(fields=FINDING_ORDERING + (('port__host', 'host'), 'port', 'name', 'version'))

    class Meta:
        '''FilterSet metadata.'''

        model = Technology
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'port': ['exact', 'isnull'],
            'port__host': ['exact'],
            'port__host__address': ['exact', 'icontains'],
            'port__host__os_type': ['exact'],
            'port__port': ['exact'],
            'name': ['exact', 'icontains'],
            'version': ['exact', 'icontains'],
            'related_to': ['exact'],
        })


class CredentialFilter(FindingFilter):
    '''FilterSet to filter and sort Credential entities.'''

    o = OrderingFilter(fields=FINDING_ORDERING + ('email', 'username'))         # Ordering fields including common ones

    class Meta:
        '''FilterSet metadata.'''

        model = Credential
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'technology': ['exact', 'isnull'],
            'technology__port': ['exact', 'isnull'],
            'technology__port__host': ['exact'],
            'technology__port__host__address': ['exact', 'icontains'],
            'technology__port__host__os_type': ['exact'],
            'technology__port__port': ['exact'],
            'technology__name': ['exact', 'icontains'],
            'technology__version': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'username': ['exact', 'icontains'],
        })


class VulnerabilityFilter(BaseVulnerabilityFilter):
    '''FilterSet to filter and sort Vulnerability entities.'''

    # Port field names to use in the filters
    port_fields: List[str] = ['technology__port', 'port']
    # Host field names to use in the filters
    host_fields: List[str] = ['technology__port__host', 'port__host']
    # Ordering fields including common ones
    o = OrderingFilter(fields=FINDING_ORDERING + ('port', 'technology', 'name', 'severity', 'cve'))

    class Meta:
        '''FilterSet metadata.'''

        model = Vulnerability
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'port': ['isnull'],
            'technology': ['exact', 'isnull'],
            'technology__name': ['exact', 'icontains'],
            'technology__version': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'severity': ['exact'],
            'cve': ['exact', 'contains'],
            'exploit': ['isnull']
        })


class ExploitFilter(BaseVulnerabilityFilter):
    '''FilterSet to filter and sort Exploit entities.'''

    # Port field names to use in the filters
    port_fields: List[str] = [
        'technology__port', 'vulnerability__port',
        'vulnerability__technology__port'
    ]
    # Host field names to use in the filters
    host_fields: List[str] = [
        'technology__port__host', 'vulnerability__port__host',
        'vulnerability__technology__port__host'
    ]
    # Ordering fields including common ones
    o = OrderingFilter(fields=FINDING_ORDERING + ('vulnerability', 'technology', 'title', 'edb_id'))

    class Meta:
        '''FilterSet metadata.'''

        model = Exploit
        fields = FINDING_FILTERING.copy()                                       # Common filtering fields
        fields.update({                                                         # Include specific filtering fields
            'vulnerability': ['exact', 'isnull'],
            'vulnerability__name': ['exact', 'icontains'],
            'vulnerability__severity': ['exact'],
            'vulnerability__cve': ['exact', 'contains'],
            'vulnerability__technology': ['exact'],
            'vulnerability__technology__name': ['exact', 'icontains'],
            'vulnerability__technology__version': ['exact', 'icontains'],
            'technology': ['exact', 'isnull'],
            'technology__name': ['exact', 'icontains'],
            'technology__version': ['exact', 'icontains'],
            'technology__port': ['exact'],
            'technology__port__host': ['exact'],
            'technology__port__host__address': ['exact', 'icontains'],
            'technology__port__host__os_type': ['exact'],
            'technology__port__port': ['exact'],
            'title': ['exact', 'icontains'],
            'edb_id': ['exact'],
            'reference': ['exact', 'icontains'],
        })

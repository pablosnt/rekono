from typing import Tuple

from django.db.models import Q, query
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from findings.enums import OSType
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)

from rekono.api.filters import ToolFilter

FINDING_ORDERING = (
    ('execution__task', 'task'),
    ('execution__task__target', 'target'),
    ('execution__task__target__project', 'project'),
    ('execution__task__tool', 'task__tool'),
    ('execution__step__tool', 'step__tool'),
    ('execution__task__executor', 'executor'),
    'execution',
    'creation',
    'is_active'
)
FINDING_FILTERING = {
    'execution': ['exact'],
    'execution__task': ['exact'],
    'execution__task__target': ['exact'],
    'execution__task__target__project': ['exact'],
    'execution__task__executor': ['exact'],
    'execution__start': ['gte', 'lte', 'exact'],
    'execution__end': ['gte', 'lte', 'exact'],
    'creation': ['gte', 'lte', 'exact'],
    'is_active': ['exact'],
}


class FindingFilter(ToolFilter):
    tool_fields: Tuple[str, str] = ('execution__task__tool', 'execution__step__tool')


class BaseVulnerabilityFilter(FindingFilter):
    enumeration = filters.NumberFilter(field_name='enumeration', method='filter_enumeration')
    enumeration_port = filters.NumberFilter(
        field_name='enumeration__port',
        method='filter_enumeration_port'
    )
    host = filters.NumberFilter(field_name='host', method='filter_host')
    host_address = filters.AllValuesFilter(field_name='host__address', method='filter_host_address')
    host_os_type = filters.ChoiceFilter(
        field_name='host__os_type',
        method='filter_host_os_type',
        choices=OSType.choices
    )
    enumeration_fields: Tuple[str, str] = ()
    enumeration_port_fields: Tuple[str, str] = ()
    host_fields: Tuple[str, str] = ()
    host_address_fields: Tuple[str, str] = ()
    host_os_type_fields: Tuple[str, str] = ()

    def filter_enumeration(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.enumeration_fields)

    def filter_enumeration_port(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.enumeration_port_fields)

    def filter_host(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.host_fields)

    def filter_host_address(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.host_address_fields)

    def filter_host_os_type(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.host_os_type_fields)


class OSINTFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + ('data', 'data_type', 'source'))

    class Meta:
        model = OSINT
        fields = FINDING_FILTERING.copy()
        fields.update({
            'data': ['exact', 'contains'],
            'data_type': ['exact'],
            'source': ['exact', 'contains'],
        })


class HostFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + ('address', 'os_type'))

    class Meta:
        model = Host
        fields = FINDING_FILTERING.copy()
        fields.update({
            'address': ['exact', 'contains'],
            'os_type': ['exact'],
        })


class EnumerationFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('host__os_type', 'os_type'), 'host', 'port', 'protocol', 'service'
    ))

    class Meta:
        model = Enumeration
        fields = FINDING_FILTERING.copy()
        fields.update({
            'host': ['exact'],
            'host__address': ['exact', 'contains'],
            'host__os_type': ['exact'],
            'port': ['exact'],
            'port_status': ['exact'],
            'protocol': ['exact'],
            'service': ['exact', 'contains'],
        })


class EndpointFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'endpoint', 'status'
    ))

    class Meta:
        model = Endpoint
        fields = FINDING_FILTERING.copy()
        fields.update({
            'enumeration': ['exact'],
            'enumeration__host': ['exact'],
            'enumeration__host__address': ['exact', 'contains'],
            'enumeration__host__os_type': ['exact'],
            'enumeration__port': ['exact'],
            'endpoint': ['exact', 'contains'],
            'status': ['exact'],
        })


class TechnologyFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'name', 'version'
    ))

    class Meta:
        model = Technology
        fields = FINDING_FILTERING.copy()
        fields.update({
            'enumeration': ['exact'],
            'enumeration__host': ['exact'],
            'enumeration__host__address': ['exact', 'contains'],
            'enumeration__host__os_type': ['exact'],
            'enumeration__port': ['exact'],
            'name': ['exact', 'contains'],
            'version': ['exact', 'contains'],
            'related_to': ['exact'],
        })


class VulnerabilityFilter(BaseVulnerabilityFilter):
    enumeration_fields: Tuple[str, str] = ('technology__enumeration', 'enumeration')
    enumeration_port_fields: Tuple[str, str] = (
        'technology__enumeration__port', 'enumeration__port'
    )
    host_fields: Tuple[str, str] = ('technology__enumeration__host', 'enumeration__host')
    host_address_fields: Tuple[str, str] = (
        'technology__enumeration__host__address', 'enumeration__host__address'
    )
    host_os_type_fields: Tuple[str, str] = (
        'technology__enumeration__host__os_type', 'enumeration__host__os_type'
    )
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'technology', 'name', 'severity', 'cve'
    ))

    class Meta:
        model = Vulnerability
        fields = FINDING_FILTERING.copy()
        fields.update({
            'technology': ['exact'],
            'technology__name': ['exact', 'contains'],
            'technology__version': ['exact', 'contains'],
            'name': ['exact', 'contains'],
            'description': ['exact', 'contains'],
            'severity': ['exact'],
            'cve': ['exact', 'contains'],
        })


class CredentialFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + ('email', 'username'))

    class Meta:
        model = Credential
        fields = FINDING_FILTERING.copy()
        fields.update({
            'email': ['exact', 'contains'],
            'username': ['exact', 'contains'],
        })


class ExploitFilter(BaseVulnerabilityFilter):
    enumeration_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration', 'vulnerability__enumeration'
    )
    enumeration_port_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration__port', 'vulnerability__enumeration__port'
    )
    host_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration__host', 'vulnerability__enumeration__host'
    )
    host_address_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration__host__address',
        'vulnerability__enumeration__host__address'
    )
    host_os_type_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration__host__os_type',
        'vulnerability__enumeration__host__os_type'
    )
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'technology', 'name'
    ))

    class Meta:
        model = Exploit
        fields = FINDING_FILTERING.copy()
        fields.update({
            'vulnerability__technology': ['exact'],
            'vulnerability__technology__name': ['exact', 'contains'],
            'vulnerability__technology__version': ['exact', 'contains'],
            'technology': ['exact'],
            'technology__name': ['exact', 'contains'],
            'technology__version': ['exact', 'contains'],
            'technology__enumeration': ['exact'],
            'technology__enumeration__host': ['exact'],
            'technology__enumeration__host__address': ['exact', 'contains'],
            'technology__enumeration__host__os_type': ['exact'],
            'technology__enumeration__port': ['exact'],
            'name': ['exact', 'contains'],
            'description': ['exact', 'contains'],
            'reference': ['exact', 'contains'],
            'checked': ['exact'],
        })

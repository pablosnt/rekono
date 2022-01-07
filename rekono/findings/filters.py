from typing import Tuple

from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from findings.enums import OSType
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)

from api.filters import ToolFilter

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
    'execution__task__target__target': ['exact', 'icontains'],
    'execution__task__target__project': ['exact'],
    'execution__task__target__project__name': ['exact', 'icontains'],
    'execution__task__executor': ['exact'],
    'execution__task__executor__username': ['exact', 'icontains'],
    'execution__start': ['gte', 'lte', 'exact'],
    'execution__end': ['gte', 'lte', 'exact'],
    'creation': ['gte', 'lte', 'exact'],
    'is_active': ['exact'],
}


class FindingFilter(ToolFilter):
    tool_fields: Tuple[str, str] = ('execution__task__tool', 'execution__step__tool')


class BaseVulnerabilityFilter(FindingFilter):
    enumeration = filters.NumberFilter(method='filter_enumeration')
    enumeration_port = filters.NumberFilter(method='filter_enumeration_port')
    host = filters.NumberFilter(method='filter_host')
    host_address = filters.CharFilter(method='filter_host_address')
    host_os_type = filters.ChoiceFilter(method='filter_host_os_type', choices=OSType.choices)
    enumeration_fields: Tuple[str, str] = ()
    host_fields: Tuple[str, str] = ()

    def filter_enumeration(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.enumeration_fields)

    def filter_enumeration_port(self, queryset, name, value):
        field1, field2 = self.enumeration_fields
        return self.multiple_field_filter(queryset, value, (f'{field1}__port', f'{field2}__port'))

    def filter_host(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.host_fields)

    def filter_host_address(self, queryset, name, value):
        field1, field2 = self.host_fields
        return self.multiple_field_filter(
            queryset, value, (f'{field1}__address', f'{field2}__address')
        )

    def filter_host_os_type(self, queryset, name, value):
        field1, field2 = self.host_fields
        return self.multiple_field_filter(
            queryset, value, (f'{field1}__os_type', f'{field2}__os_type')
        )


class OSINTFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + ('data', 'data_type', 'source'))

    class Meta:
        model = OSINT
        fields = FINDING_FILTERING.copy()
        fields.update({
            'data': ['exact', 'icontains'],
            'data_type': ['exact'],
            'source': ['exact', 'icontains'],
        })


class HostFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + ('address', 'os_type'))

    class Meta:
        model = Host
        fields = FINDING_FILTERING.copy()
        fields.update({
            'address': ['exact', 'icontains'],
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
            'host': ['exact', 'isnull'],
            'host__address': ['exact', 'icontains'],
            'host__os_type': ['exact'],
            'port': ['exact'],
            'port_status': ['iexact'],
            'protocol': ['iexact'],
            'service': ['exact', 'icontains'],
        })


class EndpointFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'endpoint', 'status'
    ))

    class Meta:
        model = Endpoint
        fields = FINDING_FILTERING.copy()
        fields.update({
            'enumeration': ['exact', 'isnull'],
            'enumeration__host': ['exact'],
            'enumeration__host__address': ['exact', 'icontains'],
            'enumeration__host__os_type': ['exact'],
            'enumeration__port': ['exact'],
            'endpoint': ['exact', 'icontains'],
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
            'enumeration': ['exact', 'isnull'],
            'enumeration__host': ['exact'],
            'enumeration__host__address': ['exact', 'icontains'],
            'enumeration__host__os_type': ['exact'],
            'enumeration__port': ['exact'],
            'name': ['exact', 'icontains'],
            'version': ['exact', 'icontains'],
            'related_to': ['exact'],
        })


class VulnerabilityFilter(BaseVulnerabilityFilter):
    enumeration_fields: Tuple[str, str] = ('technology__enumeration', 'enumeration')
    host_fields: Tuple[str, str] = ('technology__enumeration__host', 'enumeration__host')
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'technology', 'name', 'severity', 'cve'
    ))

    class Meta:
        model = Vulnerability
        fields = FINDING_FILTERING.copy()
        fields.update({
            'enumeration': ['isnull'],
            'technology': ['exact', 'isnull'],
            'technology__name': ['exact', 'icontains'],
            'technology__version': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'severity': ['exact'],
            'cve': ['exact', 'contains'],
            'exploit': ['isnull']
        })


class CredentialFilter(FindingFilter):
    o = OrderingFilter(fields=FINDING_ORDERING + ('email', 'username'))

    class Meta:
        model = Credential
        fields = FINDING_FILTERING.copy()
        fields.update({
            'email': ['exact', 'icontains'],
            'username': ['exact', 'icontains'],
        })


class ExploitFilter(BaseVulnerabilityFilter):
    enumeration_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration', 'vulnerability__enumeration'
    )
    host_fields: Tuple[str, str] = (
        'vulnerability__technology__enumeration__host', 'vulnerability__enumeration__host'
    )
    o = OrderingFilter(fields=FINDING_ORDERING + (
        ('enumeration__host', 'host'), 'enumeration', 'technology', 'name'
    ))

    class Meta:
        model = Exploit
        fields = FINDING_FILTERING.copy()
        fields.update({
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
            'technology__enumeration': ['exact'],
            'technology__enumeration__host': ['exact'],
            'technology__enumeration__host__address': ['exact', 'icontains'],
            'technology__enumeration__host__os_type': ['exact'],
            'technology__enumeration__port': ['exact'],
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'reference': ['exact', 'icontains'],
            'checked': ['exact'],
        })

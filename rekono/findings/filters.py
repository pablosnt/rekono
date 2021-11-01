from django_filters.rest_framework.filters import OrderingFilter
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
    tool_fields = ('execution__task__tool', 'execution__step__tool')


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


class VulnerabilityFilter(FindingFilter):
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
            'technology__enumeration': ['exact'],
            'technology__enumeration__host': ['exact'],
            'technology__enumeration__host__address': ['exact', 'contains'],
            'technology__enumeration__host__os_type': ['exact'],
            'technology__enumeration__port': ['exact'],
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


class ExploitFilter(FindingFilter):
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
            'vulnerability__technology__enumeration': ['exact'],
            'vulnerability__technology__enumeration__host': ['exact'],
            'vulnerability__technology__enumeration__host__address': ['exact', 'contains'],
            'vulnerability__technology__enumeration__host__os_type': ['exact'],
            'vulnerability__technology__enumeration__port': ['exact'],
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

from django_filters.filters import ModelChoiceFilter
from findings.framework.filters import FindingFilter, TriageFindingFilter
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from framework.filters import MultipleCharFilter, MultipleNumberFilter


class OSINTFilter(TriageFindingFilter):
    class Meta:
        model = OSINT
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "data": ["exact", "icontains"],
            "data_type": ["exact"],
            "source": ["exact", "icontains"],
        }


class HostFilter(FindingFilter):
    class Meta:
        model = Host
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "address": ["exact", "icontains"],
            "os": ["exact", "icontains"],
            "os_type": ["exact"],
        }


class PortFilter(FindingFilter):
    class Meta:
        model = Port
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "host": ["exact"],
            "port": ["exact"],
            "status": ["exact"],
            "protocol": ["iexact"],
            "service": ["exact", "icontains"],
        }


class PathFilter(FindingFilter):
    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        model = Path
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "port": ["exact"],
            "path": ["exact", "icontains"],
            "status": ["exact"],
            "type": ["exact"],
        }


class TechnologyFilter(FindingFilter):
    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        model = Technology
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "port": ["exact"],
            "name": ["exact", "icontains"],
            "version": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "related_to": ["exact"],
        }


class CredentialFilter(TriageFindingFilter):
    port = ModelChoiceFilter(queryset=Port.objects.all(), field_name="technology__port")
    host = ModelChoiceFilter(
        queryset=Host.objects.all(), field_name="technology__port__host"
    )

    class Meta:
        model = Credential
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "technology": ["exact"],
            "technology__name": ["exact", "icontains"],
            "technology__version": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "username": ["exact", "icontains"],
            "secret": ["exact", "icontains"],
        }


class VulnerabilityFilter(TriageFindingFilter):
    port = MultipleNumberFilter(fields=["technology__port", "port"])
    host = MultipleNumberFilter(fields=["technology__port__host", "port__host"])

    class Meta:
        model = Vulnerability
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "technology": ["exact"],
            "technology__name": ["exact", "icontains"],
            "technology__version": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "severity": ["exact"],
            "cve": ["exact", "contains"],
            "cwe": ["exact", "contains"],
            "osvdb": ["exact", "contains"],
            "trending": ["exact"],
        }


class ExploitFilter(TriageFindingFilter):
    port = MultipleNumberFilter(
        fields=[
            "technology__port",
            "vulnerability__port",
            "vulnerability__technology__port",
        ]
    )
    host = MultipleNumberFilter(
        fields=[
            "technology__port__host",
            "vulnerability__port__host",
            "vulnerability__technology__port__host",
        ]
    )
    technology = MultipleNumberFilter(
        fields=[
            "technology",
            "vulnerability__technology",
        ]
    )
    technology__name = MultipleCharFilter(
        fields=[
            "technology__name",
            "vulnerability__technology__name",
        ]
    )
    technology__version = MultipleCharFilter(
        fields=[
            "technology__version",
            "vulnerability__technology__version",
        ]
    )

    class Meta:
        model = Exploit
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "vulnerability": ["exact", "isnull"],
            "vulnerability__severity": ["exact"],
            "vulnerability__cve": ["exact"],
            "vulnerability__cwe": ["exact"],
            "vulnerability__osvdb": ["exact"],
            "title": ["exact", "icontains"],
            "edb_id": ["exact"],
            "reference": ["exact", "icontains"],
        }

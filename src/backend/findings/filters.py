from findings.framework.filters import FindingFilter
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
from framework.filters import (
    MultipleCharFilter,
    MultipleChoiceFilter,
    MultipleFieldFilterSet,
    MultipleNumberFilter,
)


class OSINTFilter(FindingFilter):
    class Meta:
        model = OSINT
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "data": ["exact", "icontains"],
                "data_type": ["exact"],
                "source": ["exact", "icontains"],
            }
        )


class HostFilter(FindingFilter):
    class Meta:
        model = Host
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "address": ["exact", "icontains"],
                "os": ["exact", "icontains"],
                "os_type": ["exact"],
            }
        )


class PortFilter(FindingFilter):
    class Meta:
        model = Port
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "host": ["exact"],
                "host__address": ["exact", "icontains"],
                "port": ["exact"],
                "status": ["exact"],
                "protocol": ["iexact"],
                "service": ["exact", "icontains"],
            }
        )


class PathFilter(FindingFilter):
    class Meta:
        model = Path
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "port": ["exact"],
                "port__host": ["exact"],
                "port__host__address": ["exact", "icontains"],
                "port__port": ["exact"],
                "path": ["exact", "icontains"],
                "status": ["exact"],
                "type": ["exact"],
            }
        )


class TechnologyFilter(FindingFilter):
    class Meta:
        model = Technology
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "port": ["exact"],
                "port__host": ["exact"],
                "port__host__address": ["exact", "icontains"],
                "port__port": ["exact"],
                "name": ["exact", "icontains"],
                "version": ["exact", "icontains"],
                "description": ["exact", "icontains"],
                "related_to": ["exact"],
            }
        )


class CredentialFilter(FindingFilter):
    class Meta:
        model = Credential
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "technology": ["exact"],
                "technology__port": ["exact"],
                "technology__port__host": ["exact"],
                "technology__port__host__address": ["exact", "icontains"],
                "technology__port__port": ["exact"],
                "technology__name": ["exact", "icontains"],
                "technology__version": ["exact", "icontains"],
                "email": ["exact", "icontains"],
                "username": ["exact", "icontains"],
                "secret": ["exact", "icontains"],
            }
        )


class VulnerabilityFilter(FindingFilter):
    port = MultipleNumberFilter(fields=["technology__port", "port"])
    port__port = MultipleNumberFilter(fields=["technology__port__port", "port__port"])
    host = MultipleNumberFilter(fields=["technology__port__host", "port__host"])
    host__address = MultipleCharFilter(
        fields=["technology__port__host__address", "port__host__address"]
    )
    host__os_type = MultipleChoiceFilter(
        fields=["technology__port__host__os_type", "port__host__os_type"]
    )

    class Meta:
        model = Vulnerability
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "technology": ["exact"],
                "technology__name": ["exact", "icontains"],
                "technology__version": ["exact", "icontains"],
                "name": ["exact", "icontains"],
                "description": ["exact", "icontains"],
                "severity": ["exact"],
                "cve": ["exact", "contains"],
                "cwe": ["exact", "contains"],
                "osvdb": ["exact", "contains"],
            }
        )


class ExploitFilter(FindingFilter):
    port = MultipleNumberFilter(
        fields=[
            "technology__port",
            "vulnerability__port",
            "vulnerability__technology__port",
        ]
    )
    port__port = MultipleNumberFilter(
        fields=[
            "technology__port__port",
            "vulnerability__port__port",
            "vulnerability__technology__port__port",
        ]
    )
    host = MultipleNumberFilter(
        fields=[
            "technology__port__host",
            "vulnerability__port__host",
            "vulnerability__technology__port__host",
        ]
    )
    host__address = MultipleCharFilter(
        fields=[
            "technology__port__host__address",
            "vulnerability__port__host__address",
            "vulnerability__technology__port__host__address",
        ]
    )
    host__os_type = MultipleChoiceFilter(
        fields=[
            "technology__port__host__os_type",
            "vulnerability__port__host__os_type",
            "vulnerability__technology__port__host__os_type",
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
        fields = FindingFilter.Meta.fields.copy()
        fields.update(
            {
                "vulnerability": ["exact"],
                "vulnerability__name": ["exact", "icontains"],
                "vulnerability__severity": ["exact"],
                "vulnerability__cve": ["exact", "contains"],
                "vulnerability__cwe": ["exact", "contains"],
                "vulnerability__osvdb": ["exact", "contains"],
                "title": ["exact", "icontains"],
                "edb_id": ["exact"],
                "reference": ["exact", "icontains"],
            }
        )

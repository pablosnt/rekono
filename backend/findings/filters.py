"""Filters of the finding endpoints.

Besides their own fields, the findings can be filtered by the ones where they were
discovered, even if they aren't directly related to them, so all the findings can
be searched by host and port no matter how deep they are in the finding chain.
"""

from django_filters.filters import CharFilter, ModelChoiceFilter

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
    """Filters to search the data found on public sources."""

    class Meta:
        """Filter configuration adding the OSINT fields to the common ones."""

        model = OSINT
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "data": ["exact", "icontains"],
            "data_type": ["exact"],
            "source": ["exact", "icontains"],
        }


class HostFilter(FindingFilter):
    """Filters to search the hosts found in the network."""

    class Meta:
        """Filter configuration adding the host fields to the common ones."""

        model = Host
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "ip": ["exact", "icontains"],
            "domain": ["exact", "icontains"],
            "os": ["exact", "icontains"],
            "os_type": ["exact"],
            "country": ["exact", "icontains"],
            "city": ["exact", "icontains"],
            "latitude": ["isnull"],
            "longitude": ["isnull"],
        }


class PortFilter(FindingFilter):
    """Filters to search the ports found in the hosts."""

    class Meta:
        """Filter configuration adding the port fields to the common ones."""

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
    """Filters to search the paths found in the ports.

    Attributes:
        host: Filter by the host of the port where the path was found.
    """

    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        """Filter configuration adding the path fields to the common ones."""

        model = Path
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "port": ["exact"],
            "path": ["exact", "icontains"],
            "status": ["exact"],
            "type": ["exact"],
        }


class TechnologyFilter(FindingFilter):
    """Filters to search the technologies found in the ports.

    Attributes:
        host: Filter by the host of the port where the technology was found.
    """

    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        """Filter configuration adding the technology fields to the common ones."""

        model = Technology
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "port": ["exact"],
            "name": ["exact", "icontains"],
            "version": ["exact", "icontains"],
            "description": ["exact", "icontains"],
        }


class CredentialFilter(TriageFindingFilter):
    """Filters to search the credentials exposed in the technologies.

    Attributes:
        port: Filter by the port of the technology that exposed the credential.
        host: Filter by the host of that port.
    """

    port = ModelChoiceFilter(queryset=Port.objects.all(), field_name="technology__port")
    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="technology__port__host")

    class Meta:
        """Filter configuration adding the credential fields to the common ones."""

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
    """Filters to search the vulnerabilities found in the technologies and ports.

    Attributes:
        port: Filter by the port where the vulnerability was found, directly or
          through its technology.
        host: Filter by the host of that port.
        cwe: Filter by one of the CWE identifiers of the vulnerability.
    """

    port = MultipleNumberFilter(fields=["technology__port", "port"])
    host = MultipleNumberFilter(fields=["technology__port__host", "port__host"])
    cwe = CharFilter(field_name="cwes", lookup_expr="icontains")

    class Meta:
        """Filter configuration adding the vulnerability fields to the common ones."""

        model = Vulnerability
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "technology": ["exact"],
            "technology__name": ["exact", "icontains"],
            "technology__version": ["exact", "icontains"],
            "port": ["exact"],
            "name": ["exact", "icontains"],
            "description": ["exact", "icontains"],
            "severity": ["exact"],
            "cvss_version": ["exact"],
            "cvss_base_score": ["gte", "lte", "exact"],
            "epss_score": ["gte", "lte"],
            "epss_percentile": ["gte", "lte"],
            "cve": ["exact"],
            "euvd_id": ["exact"],
            "ghsa_id": ["exact"],
            "osv_generic_id": ["exact"],
            "trending": ["exact"],
        }


class ExploitFilter(TriageFindingFilter):
    """Filters to search the exploits found for the vulnerabilities and technologies.

    Attributes:
        port: Filter by the port where the exploit was found, through its technology
          or through its vulnerability.
        host: Filter by the host of that port.
        technology: Filter by the technology that the exploit targets, directly or
          through its vulnerability.
        technology__name: Filter by the name of that technology.
        technology__version: Filter by the version of that technology.
        vulnerability__cwe: Filter by one of the CWE identifiers of the vulnerability
          that the exploit takes advantage of.
    """

    port = MultipleNumberFilter(fields=["technology__port", "vulnerability__port", "vulnerability__technology__port"])
    host = MultipleNumberFilter(
        fields=["technology__port__host", "vulnerability__port__host", "vulnerability__technology__port__host"]
    )
    technology = MultipleNumberFilter(fields=["technology", "vulnerability__technology"])
    technology__name = MultipleCharFilter(fields=["technology__name", "vulnerability__technology__name"])
    technology__version = MultipleCharFilter(fields=["technology__version", "vulnerability__technology__version"])
    vulnerability__cwe = CharFilter(field_name="vulnerability__cwes", lookup_expr="icontains")

    class Meta:
        """Filter configuration adding the exploit fields to the common ones."""

        model = Exploit
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "vulnerability": ["exact"],
            "vulnerability__name": ["exact", "icontains"],
            "vulnerability__severity": ["exact"],
            "vulnerability__cve": ["exact"],
            "vulnerability__euvd_id": ["exact"],
            "vulnerability__ghsa_id": ["exact"],
            "vulnerability__osv_generic_id": ["exact"],
            "title": ["exact", "icontains"],
            "edb_id": ["exact"],
            "reference": ["exact", "icontains"],
        }

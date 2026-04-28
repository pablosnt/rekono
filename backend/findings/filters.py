"""Filters for findings models and REST API search capabilities.

Provides filter classes for all finding types enabling advanced filtering
and search operations through the REST API with field-specific filter
configurations and relationship-based filtering.
"""

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
    """Filter for Open Source Intelligence findings.

    Enables filtering and search operations for OSINT findings based on
    data content, data type classification, and source information.
    """

    class Meta:
        """Meta configuration for OSINTFilter.

        Defines filterable fields and lookup types for OSINT findings
        with exact match and case-insensitive contains operations.

        Attributes:
            model (type): OSINT model class.
            fields (dict): Field names mapped to available lookup types.
        """

        model = OSINT
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "data": ["exact", "icontains"],
            "data_type": ["exact"],
            "source": ["exact", "icontains"],
        }


class HostFilter(FindingFilter):
    """Filter for network host findings.

    Enables filtering and search operations for network hosts based on
    IP addresses, domains, operating systems, and geolocation data.
    """

    class Meta:
        """Meta configuration for HostFilter.

        Defines filterable fields and lookup types for host findings
        including geolocation and operating system filtering.

        Attributes:
            model (type): Host model class.
            fields (dict): Field names mapped to available lookup types.
        """

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
    """Filter for network port findings.

    Enables filtering and search operations for network ports based on
    host relationships, port numbers, status, protocols, and services.
    """

    class Meta:
        """Meta configuration for PortFilter.

        Defines filterable fields and lookup types for port findings
        including protocol and service identification filtering.

        Attributes:
            model (type): Port model class.
            fields (dict): Field names mapped to available lookup types.
        """

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
    """Filter for web path findings.

    Enables filtering and search operations for web paths based on
    associated ports, path content, HTTP status, and resource types.

    Attributes:
        host (ModelChoiceFilter): Filter by host through port relationship
    """

    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        """Meta configuration for PathFilter.

        Defines filterable fields and lookup types for path findings
        including HTTP status codes and resource type classification.

        Attributes:
            model (type): Path model class.
            fields (dict): Field names mapped to available lookup types.
        """

        model = Path
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "port": ["exact"],
            "path": ["exact", "icontains"],
            "status": ["exact"],
            "type": ["exact"],
        }


class TechnologyFilter(FindingFilter):
    """Filter for technology findings.

    Enables filtering and search operations for software technologies
    based on associated ports, technology names, versions, and descriptions.

    Attributes:
        host (ModelChoiceFilter): Filter by host through port relationship
    """

    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        """Meta configuration for TechnologyFilter.

        Defines filterable fields and lookup types for technology findings
        including version matching and description search capabilities.

        Attributes:
            model (type): Technology model class.
            fields (dict): Field names mapped to available lookup types.
        """

        model = Technology
        fields = {
            **FindingFilter.Meta.fields.copy(),
            "port": ["exact"],
            "name": ["exact", "icontains"],
            "version": ["exact", "icontains"],
            "description": ["exact", "icontains"],
        }


class CredentialFilter(TriageFindingFilter):
    """Filter for credential findings.

    Enables filtering and search operations for credentials based on
    associated technologies, email addresses, usernames, and secrets.

    Attributes:
        port (ModelChoiceFilter): Filter by port through technology
        host (ModelChoiceFilter): Filter by host through technology port
    """

    port = ModelChoiceFilter(queryset=Port.objects.all(), field_name="technology__port")
    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="technology__port__host")

    class Meta:
        """Meta configuration for CredentialFilter.

        Defines filterable fields and lookup types for credential findings
        including technology relationship filtering and credential data search.

        Attributes:
            model (type): Credential model class.
            fields (dict): Field names mapped to available lookup types.
        """

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
    """Filter for vulnerability findings.

    Enables filtering and search operations for vulnerabilities based on
    technologies, ports, CVE/CWE identifiers, severity, and trending status.

    Attributes:
        port (MultipleNumberFilter): Filter by port through technology or direct
        host (MultipleNumberFilter): Filter by host through tech port or direct
    """

    port = MultipleNumberFilter(fields=["technology__port", "port"])
    host = MultipleNumberFilter(fields=["technology__port__host", "port__host"])

    class Meta:
        """Meta configuration for VulnerabilityFilter.

        Defines filterable fields and lookup types for vulnerability findings
        including CVE/CWE matching, severity levels, and trending indicators.

        Attributes:
            model (type): Vulnerability model class.
            fields (dict): Field names mapped to available lookup types.
        """

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
            "cve": ["exact", "icontains"],
            "cwe": ["exact", "icontains"],
            "trending": ["exact"],
        }


class ExploitFilter(TriageFindingFilter):
    """Filter for exploit findings.

    Enables filtering and search operations for exploits based on
    associated vulnerabilities, technologies, titles, and database identifiers.

    Attributes:
        port (MultipleNumberFilter): Filter by port through tech or vuln
        host (MultipleNumberFilter): Filter by host through tech or vuln port
        technology (MultipleNumberFilter): Filter by tech through direct or vuln
        technology__name (MultipleCharFilter): Filter by tech name through direct/vuln
        technology__version (MultipleCharFilter): Filter by tech version direct/vuln
    """

    port = MultipleNumberFilter(fields=["technology__port", "vulnerability__port", "vulnerability__technology__port"])
    host = MultipleNumberFilter(
        fields=["technology__port__host", "vulnerability__port__host", "vulnerability__technology__port__host"]
    )
    technology = MultipleNumberFilter(fields=["technology", "vulnerability__technology"])
    technology__name = MultipleCharFilter(fields=["technology__name", "vulnerability__technology__name"])
    technology__version = MultipleCharFilter(fields=["technology__version", "vulnerability__technology__version"])

    class Meta:
        """Meta configuration for ExploitFilter.

        Defines filterable fields and lookup types for exploit findings
        including vulnerability relationships and exploit database references.

        Attributes:
            model (type): Exploit model class.
            fields (dict): Field names mapped to available lookup types.
        """

        model = Exploit
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "vulnerability": ["exact"],
            "vulnerability__name": ["exact", "icontains"],
            "vulnerability__severity": ["exact"],
            "vulnerability__cve": ["exact", "icontains"],
            "vulnerability__cwe": ["exact", "icontains"],
            "title": ["exact", "icontains"],
            "edb_id": ["exact"],
            "reference": ["exact", "icontains"],
        }

"""Django filters for findings models.

This module provides filter classes for all finding types, enabling
advanced filtering and search capabilities through the REST API.
Each filter extends the base finding filters to provide standardized
functionality while allowing for custom filtering behavior specific
to each finding type.
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
    """Filter for OSINT findings.

    Provides filtering capabilities for OSINT data based on data content,
    data type, and source information.
    """

    class Meta:
        """Meta configuration for the OSINTFilter.

        Attributes:
            model: The OSINT model to filter.
            fields: The fields to filter.
        """

        model = OSINT
        fields = {
            **TriageFindingFilter.Meta.fields.copy(),
            "data": ["exact", "icontains"],
            "data_type": ["exact"],
            "source": ["exact", "icontains"],
        }


class HostFilter(FindingFilter):
    """Filter for host findings.

    Provides filtering capabilities for host data based on IP address,
    domain, operating system, and geolocation information.
    """

    class Meta:
        """Meta configuration for the HostFilter.

        Attributes:
            model: The Host model to filter.
            fields: The fields to filter.
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
        }


class PortFilter(FindingFilter):
    """Filter for port findings.

    Provides filtering capabilities for port data based on host,
    port number, status, protocol, and service information.
    """

    class Meta:
        """Meta configuration for the PortFilter.

        Attributes:
            model: The Port model to filter.
            fields: The fields to filter.
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
    """Filter for path findings.

    Provides filtering capabilities for path data based on port,
    path content, status, and type information.
    """

    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        """Meta configuration for the PathFilter.

        Attributes:
            model: The Path model to filter.
            fields: The fields to filter.
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

    Provides filtering capabilities for technology data based on port,
    name, version, and description information.
    """

    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="port__host")

    class Meta:
        """Meta configuration for the TechnologyFilter.

        Attributes:
            model: The Technology model to filter.
            fields: The fields to filter.
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

    Provides filtering capabilities for credential data based on technology,
    email, username, and secret information.
    """

    port = ModelChoiceFilter(queryset=Port.objects.all(), field_name="technology__port")
    host = ModelChoiceFilter(queryset=Host.objects.all(), field_name="technology__port__host")

    class Meta:
        """Meta configuration for the CredentialFilter.

        Attributes:
            model: The Credential model to filter.
            fields: The fields to filter.
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

    Provides filtering capabilities for vulnerability data based on technology,
    port, name, description, CVE, CWE, and severity information.
    """

    port = MultipleNumberFilter(fields=["technology__port", "port"])
    host = MultipleNumberFilter(fields=["technology__port__host", "port__host"])

    class Meta:
        """Meta configuration for the VulnerabilityFilter.

        Attributes:
            model: The Vulnerability model to filter.
            fields: The fields to filter.
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
            "cve": ["exact", "icontains"],
            "cwe": ["exact", "icontains"],
            "trending": ["exact"],
        }


class ExploitFilter(TriageFindingFilter):
    """Filter for exploit findings.

    Provides filtering capabilities for exploit data based on vulnerability,
    technology, title, EDB ID, and reference information.
    """

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
        """Meta configuration for the ExploitFilter.

        Attributes:
            model: The Exploit model to filter.
            fields: The fields to filter.
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

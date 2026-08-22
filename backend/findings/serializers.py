"""Serializers of the finding endpoints.

Each finding type has a serializer with all its data, including the findings that
are related to it, and the ones that can be nested in another finding also have a
simple serializer that only includes their own fields, so the responses don't grow
indefinitely by following the relations in both directions.
"""

from typing import Any

from rest_framework.serializers import CharField, ListField, ModelSerializer

from findings.enums import Severity, TriageStatus
from findings.framework.serializers import (
    FindingSerializer,
    HacktricksFindingSerializer,
    TriageFindingSerializer,
)
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
from framework.fields import IntegerChoicesField


class OSINTSerializer(TriageFindingSerializer):
    """Serializer of the data found on public sources."""

    class Meta:
        """Serializer configuration adding the OSINT fields to the common ones."""

        model = OSINT
        fields = TriageFindingSerializer.Meta.fields + ("data", "data_type", "source")
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "data",
            "data_type",
            "source",
        )


class SimpleHostSerializer(ModelSerializer):
    """Serializer of a host to be included in other findings."""

    class Meta:
        """Serializer configuration including only the host fields."""

        model = Host
        fields = (
            "id",
            "ip",
            "domain",
            "os",
            "os_type",
            "country",
            "city",
            "latitude",
            "longitude",
            "reputation",
            "malicious_analysis",
            "suspicious_analysis",
            "total_analysis",
            "whois",
        )


class HostSerializer(HacktricksFindingSerializer):
    """Serializer of a host, including the ports found on it."""

    class Meta:
        """Serializer configuration adding the host fields to the common ones."""

        model = Host
        fields = HacktricksFindingSerializer.Meta.fields + SimpleHostSerializer.Meta.fields + ("port",)


class SimplePortSerializer(ModelSerializer):
    """Serializer of a port to be included in other findings.

    Attributes:
        host: Host where the port was found.
    """

    host = SimpleHostSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration including only the port fields."""

        model = Port
        fields = (
            "id",
            "host",
            "port",
            "status",
            "protocol",
            "service",
        )


class PortSerializer(HacktricksFindingSerializer, SimplePortSerializer):
    """Serializer of a port, including the findings discovered on it."""

    class Meta:
        """Serializer configuration adding the port fields to the common ones."""

        model = Port
        fields = (
            HacktricksFindingSerializer.Meta.fields
            + SimplePortSerializer.Meta.fields
            + ("path", "technology", "vulnerability")
        )


class PathSerializer(FindingSerializer):
    """Serializer of a path found on a port.

    Attributes:
        port: Port where the path was found.
    """

    port = SimplePortSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration adding the path fields to the common ones."""

        model = Path
        fields = FindingSerializer.Meta.fields + (
            "port",
            "path",
            "status",
            "extra_info",
            "type",
        )


class SimpleTechnologySerializer(ModelSerializer):
    """Serializer of a technology to be included in other findings.

    Attributes:
        port: Port where the technology was found.
    """

    port = SimplePortSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration including only the technology fields."""

        model = Technology
        fields = ("id", "port", "name", "version", "description")


class TechnologySerializer(HacktricksFindingSerializer, SimpleTechnologySerializer):
    """Serializer of a technology, including the findings discovered on it."""

    class Meta:
        """Serializer configuration adding the technology fields to the common ones."""

        model = Technology
        fields = (
            HacktricksFindingSerializer.Meta.fields
            + SimpleTechnologySerializer.Meta.fields
            + ("credential", "vulnerability", "exploit")
        )


class CredentialSerializer(TriageFindingSerializer):
    """Serializer of a credential exposed in a technology.

    Attributes:
        technology: Technology where the credential was exposed.
    """

    technology = SimpleTechnologySerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration adding the credential fields to the common ones."""

        model = Credential
        fields = TriageFindingSerializer.Meta.fields + (
            "technology",
            "email",
            "username",
            "secret",
            "context",
        )
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "technology",
            "email",
            "username",
            "secret",
            "context",
        )


class SimpleVulnerabilitySerializer(ModelSerializer):
    """Serializer of a vulnerability to be included in other findings.

    Attributes:
        port: Port where the vulnerability was found.
        technology: Technology where the vulnerability was found.
        severity: Severity as its name instead of as the number that is stored.
        cwes: CWE identifiers of the weaknesses behind the vulnerability.
    """

    port = SimplePortSerializer(many=False, read_only=True)
    technology = SimpleTechnologySerializer(many=False, read_only=True)
    severity = IntegerChoicesField(model=Severity, required=False)
    cwes = ListField(child=CharField(), read_only=True)

    class Meta:
        """Serializer configuration including only the vulnerability fields."""

        model = Vulnerability
        fields = (
            "id",
            "port",
            "technology",
            "name",
            "description",
            "severity",
            "cvss_version",
            "cvss_vector",
            "cvss_base_score",
            "cve",
            "euvd_id",
            "ghsa_id",
            "osv_generic_id",
            "cwes",
            "epss_score",
            "epss_percentile",
            "remediation",
            "reference",
            "trending",
        )


class VulnerabilitySerializer(TriageFindingSerializer, SimpleVulnerabilitySerializer):
    """Serializer of a vulnerability, including the exploits that take advantage of it."""

    class Meta:
        """Serializer configuration adding the vulnerability fields to the common ones."""

        model = Vulnerability
        fields = TriageFindingSerializer.Meta.fields + SimpleVulnerabilitySerializer.Meta.fields + ("exploit",)
        read_only_fields = (
            TriageFindingSerializer.Meta.read_only_fields + SimpleVulnerabilitySerializer.Meta.fields + ("exploit",)
        )

    def update(self, instance: Vulnerability, validated_data: dict[str, Any]) -> Vulnerability:
        """Update the triage of a vulnerability and of its exploits.

        Args:
            instance: Vulnerability being triaged.
            validated_data: Triage fields, including the triage_date and the
              triage_by that the base validate method adds, since they are read
              only fields that the users never send.

        Returns:
            The updated vulnerability. Its exploits are triaged as false positives
            too, and they are untriaged again if the vulnerability stops being a
            false positive, but only if nobody triaged them in the meantime.
        """
        original_triage_status = instance.triage_status
        instance = super().update(instance, validated_data)
        # This is the only case of two related finding types that can be triaged
        if original_triage_status != instance.triage_status:
            exploits_triage_comment = (
                "Automatically triaged after triaging the related vulnerability as a false positive"
            )
            exploits_queryset = None
            if instance.triage_status == TriageStatus.FALSE_POSITIVE:
                exploits_triage_status = TriageStatus.FALSE_POSITIVE
                exploits_queryset = instance.exploit.all()
            elif original_triage_status == TriageStatus.FALSE_POSITIVE:
                exploits_triage_status = TriageStatus.UNTRIAGED
                exploits_queryset = instance.exploit.filter(
                    triage_status=TriageStatus.FALSE_POSITIVE, triage_comment=exploits_triage_comment
                )
                exploits_triage_comment = f"Automatically untriaged after changing the triage status for the related vulnerability to {instance.triage_status}"
            if exploits_queryset is not None:
                exploits_queryset.update(
                    triage_status=exploits_triage_status,
                    triage_comment=exploits_triage_comment,
                    triage_by=instance.triage_by,
                    triage_date=instance.triage_date,
                )
        return instance


class ExploitSerializer(TriageFindingSerializer):
    """Serializer of an exploit found for a vulnerability or a technology.

    Attributes:
        vulnerability: Vulnerability that the exploit takes advantage of.
        technology: Technology that the exploit targets.
    """

    vulnerability = SimpleVulnerabilitySerializer(many=False, read_only=True)
    technology = SimpleTechnologySerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration adding the exploit fields to the common ones."""

        model = Exploit
        fields = TriageFindingSerializer.Meta.fields + (
            "vulnerability",
            "technology",
            "title",
            "edb_id",
            "reference",
        )
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "vulnerability",
            "technology",
            "title",
            "edb_id",
            "reference",
        )

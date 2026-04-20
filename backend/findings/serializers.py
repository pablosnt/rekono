"""Serializers for findings models and REST API data conversion.

Provides serializer classes for all finding types handling conversion
between Django model instances and JSON data with validation, field
configuration, and custom update logic.
"""

from typing import Any

from rest_framework.serializers import ModelSerializer

from findings.enums import Severity, TriageStatus
from findings.framework.serializers import FindingSerializer, TriageFindingSerializer
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
    """Serializer for Open Source Intelligence findings.

    Handles JSON conversion for OSINT findings with data validation
    and read-only field configuration for API responses.
    """

    class Meta:
        """Meta configuration for OSINTSerializer.

        Defines field inclusion and read-only restrictions for OSINT
        findings serialization extending TriageFindingSerializer.

        Attributes:
            model (type): OSINT model class.
            fields (tuple): Included serializer fields.
            read_only_fields (tuple): Fields restricted from modification.
        """

        model = OSINT
        fields = TriageFindingSerializer.Meta.fields + ("data", "data_type", "source")
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "data",
            "data_type",
            "source",
        )


class SimpleHostSerializer(ModelSerializer):
    """Serializer for network host findings.

    Handles JSON conversion for network host findings for complete
    host inventory. Does not include nested port data; use HostSerializer
    when port relationships are needed.
    """

    class Meta:
        """Meta configuration for SimpleHostSerializer.

        Defines field inclusion for host findings serialization
        including geolocation data without nested port relationships.

        Attributes:
            model (type): Host model class.
            fields (tuple): Included serializer fields for host data.
        """

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


class HostSerializer(FindingSerializer):
    """Serializer for network host findings with nested port data.

    Extends FindingSerializer with SimpleHostSerializer fields to include
    host data and nested port relationships for complete host inventory.
    """

    class Meta:
        """Meta configuration for HostSerializer.

        Defines field inclusion for host findings serialization combining
        base finding fields, host data, and nested port relationships.

        Attributes:
            model (type): Host model class.
            fields (tuple): Included serializer fields with port relations.
        """

        model = Host
        fields = FindingSerializer.Meta.fields + SimpleHostSerializer.Meta.fields + ("port",)


class SimplePortSerializer(ModelSerializer):
    """Serializer for network port findings.

    Handles JSON conversion for network port findings with nested
    relationship serialization for comprehensive port data.
    """

    host = SimpleHostSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for SimplePortSerializer.

        Defines field inclusion for port findings serialization
        with a nested host relationship without finding base fields.

        Attributes:
            model (type): Port model class.
            fields (tuple): Included serializer fields with host relation.
        """

        model = Port
        fields = (
            "id",
            "host",
            "port",
            "status",
            "protocol",
            "service",
        )


class PortSerializer(FindingSerializer, SimplePortSerializer):
    """Serializer for network port findings with nested host data.

    Extends FindingSerializer with SimplePortSerializer fields to include
    the nested host object and relationships to paths, technologies,
    and vulnerabilities for complete port inventory.
    """

    class Meta:
        """Meta configuration for PortSerializer.

        Defines field inclusion for port findings serialization combining
        base finding fields, port data, and nested entity relationships.

        Attributes:
            model (type): Port model class.
            fields (tuple): Included serializer fields with relationships.
        """

        model = Port
        fields = (
            FindingSerializer.Meta.fields + SimplePortSerializer.Meta.fields + ("path", "technology", "vulnerability")
        )


class PathSerializer(FindingSerializer):
    """Serializer for web path findings.

    Handles JSON conversion for web path findings with endpoint
    and file share classification for web application analysis.

    Attributes:
        port (SimplePortSerializer): Nested port relationship (read-only)
    """

    port = SimplePortSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for PathSerializer.

        Defines field inclusion for path findings serialization
        with HTTP status and resource type classification.

        Attributes:
            model (type): Path model class.
            fields (tuple): Included serializer fields for web paths.
        """

        model = Path
        fields = FindingSerializer.Meta.fields + (
            "port",
            "path",
            "status",
            "extra_info",
            "type",
        )


class SimpleTechnologySerializer(ModelSerializer):
    """Serializer for technology findings.

    Handles JSON conversion for technology findings with a nested
    port relationship for technology stack analysis. Does not include
    finding base fields; use TechnologySerializer when those are needed.

    Attributes:
        port (SimplePortSerializer): Nested port relationship (read-only)
    """

    port = SimplePortSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for SimpleTechnologySerializer.

        Defines field inclusion for technology findings serialization
        with a nested port relationship and core technology attributes.

        Attributes:
            model (type): Technology model class.
            fields (tuple): Included serializer fields with port relation.
        """

        model = Technology
        fields = ("id", "port", "name", "version", "description")


class TechnologySerializer(FindingSerializer, SimpleTechnologySerializer):
    """Serializer for technology findings with full relationship data.

    Extends FindingSerializer with SimpleTechnologySerializer fields to include
    nested port data and relationships to credentials, vulnerabilities,
    and exploits for complete technology stack analysis.
    """

    class Meta:
        """Meta configuration for TechnologySerializer.

        Defines field inclusion for technology findings serialization combining
        base finding fields, technology data, and nested entity relationships.

        Attributes:
            model (type): Technology model class.
            fields (tuple): Included serializer fields with nested relations.
        """

        model = Technology
        fields = (
            FindingSerializer.Meta.fields
            + SimpleTechnologySerializer.Meta.fields
            + ("credential", "vulnerability", "exploit")
        )


class CredentialSerializer(TriageFindingSerializer):
    """Serializer for credential findings.

    Handles JSON conversion for credential findings with read-only
    restrictions for sensitive authentication data protection.
    """

    class Meta:
        """Meta configuration for CredentialSerializer.

        Defines field inclusion and read-only restrictions for credential
        findings to prevent unauthorized modification of sensitive data.

        Attributes:
            model (type): Credential model class.
            fields (tuple): Included serializer fields for credentials.
            read_only_fields (tuple): Protected credential data fields.
        """

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
    """Serializer for vulnerability findings.

    Handles JSON conversion for vulnerability findings with nested port
    and technology relationships for vulnerability assessment. Does not
    include finding base fields; use VulnerabilitySerializer when those
    are needed.

    Attributes:
        port (SimplePortSerializer): Nested port relationship (read-only)
        technology (SimpleTechnologySerializer): Nested technology relationship (read-only)
        severity (IntegerChoicesField): Severity level choice field
    """

    port = SimplePortSerializer(many=False, read_only=True)
    technology = SimpleTechnologySerializer(many=False, read_only=True)
    severity = IntegerChoicesField(model=Severity, required=False)

    class Meta:
        """Meta configuration for SimpleVulnerabilitySerializer.

        Defines field inclusion for vulnerability findings serialization
        with nested port and technology relationships and CVE/CWE mapping.

        Attributes:
            model (type): Vulnerability model class.
            fields (tuple): Included serializer fields for vulnerabilities.
        """

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
            "cwe",
            "remediation",
            "reference",
            "trending",
        )


class VulnerabilitySerializer(TriageFindingSerializer, SimpleVulnerabilitySerializer):
    """Serializer for vulnerability findings.

    Handles JSON conversion for vulnerability findings with severity
    field handling and automatic exploit triage on status updates.
    Inherits nested port, technology, and severity fields from
    SimpleVulnerabilitySerializer.
    """

    class Meta:
        """Meta configuration for VulnerabilitySerializer.

        Defines field inclusion and read-only restrictions for vulnerability
        findings with CVE/CWE mapping and severity classification.

        Attributes:
            model (type): Vulnerability model class.
            fields (tuple): Included serializer fields for vulnerabilities.
            read_only_fields (tuple): Protected vulnerability data fields.
        """

        model = Vulnerability
        fields = TriageFindingSerializer.Meta.fields + SimpleVulnerabilitySerializer.Meta.fields + ("exploit",)
        read_only_fields = (
            TriageFindingSerializer.Meta.read_only_fields + SimpleVulnerabilitySerializer.Meta.fields + ("exploit",)
        )

    def update(self, instance: Vulnerability, validated_data: dict[str, Any]) -> Vulnerability:
        """Update vulnerability with automatic exploit triage handling.

        Updates vulnerability findings and automatically triages related
        exploits when vulnerability triage status changes.

        Args:
            instance (Vulnerability): Vulnerability instance to update.
            validated_data (dict[str, Any]): Validated update data.

        Returns:
            Vulnerability: Updated vulnerability with triage propagation.
        """
        original_triage_status = instance.triage_status
        instance = super().update(instance, validated_data)
        # This is the only case of two related finding types that can be triaged
        if original_triage_status != instance.triage_status:
            exploits_triage_comment = (
                "Automatically triaged after triaging the related vulnerability as a false positive"
            )
            if instance.triage_status == TriageStatus.FALSE_POSITIVE:
                exploits_triage_status = TriageStatus.FALSE_POSITIVE
                exploits_queryset = instance.exploit.all()
            elif original_triage_status == TriageStatus.FALSE_POSITIVE:
                exploits_triage_status = TriageStatus.UNTRIAGED
                exploits_queryset = instance.exploit.filter(
                    triage_status=TriageStatus.FALSE_POSITIVE, triage_comment=exploits_triage_comment
                )
                exploits_triage_comment = (
                    "Automatically untriaged after a triage status change on the related vulnerability"
                )
            exploits_queryset.update(
                triage_status=exploits_triage_status,
                triage_comment=exploits_triage_comment,
                triage_by=instance.triage_by,
                triage_date=instance.triage_date,
            )
        return instance


class ExploitSerializer(TriageFindingSerializer):
    """Serializer for exploit findings.

    Handles JSON conversion for exploit findings with read-only
    restrictions for exploit database references and links.

    Attributes:
        vulnerability (SimpleVulnerabilitySerializer): Nested vulnerability relationship (read-only)
        technology (SimpleTechnologySerializer): Nested technology relationship (read-only)
    """

    vulnerability = SimpleVulnerabilitySerializer(many=False, read_only=True)
    technology = SimpleTechnologySerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for ExploitSerializer.

        Defines field inclusion and read-only restrictions for exploit
        findings to prevent modification of exploit database references.

        Attributes:
            model (type): Exploit model class.
            fields (tuple): Included serializer fields for exploits.
            read_only_fields (tuple): Protected exploit reference fields.
        """

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

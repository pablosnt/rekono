"""Serializers for findings models and REST API data conversion.

Provides serializer classes for all finding types handling conversion
between Django model instances and JSON data with validation, field
configuration, and custom update logic.
"""

from typing import Any

from findings.enums import Severity
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


class PortSerializer(FindingSerializer):
    """Serializer for network port findings.

    Handles JSON conversion for network port findings with nested
    relationship serialization for comprehensive port data.
    """

    class Meta:
        """Meta configuration for PortSerializer.

        Defines field inclusion for port findings serialization
        with nested relationships for complete port information.

        Attributes:
            model (type): Port model class.
            fields (tuple): Included serializer fields with relationships.
        """

        model = Port
        fields = FindingSerializer.Meta.fields + (
            "host",
            "port",
            "status",
            "protocol",
            "service",
            "path",
            "technology",
            "vulnerability",
        )


class HostSerializer(FindingSerializer):
    """Serializer for network host findings.

    Handles JSON conversion for network host findings with nested
    port relationship serialization for complete host inventory.

    Attributes:
        port (PortSerializer): Nested port relationships (read-only)
    """

    port = PortSerializer(many=True, read_only=True)

    class Meta:
        """Meta configuration for HostSerializer.

        Defines field inclusion for host findings serialization
        including geolocation and nested port relationships.

        Attributes:
            model (type): Host model class.
            fields (tuple): Included serializer fields with port relations.
        """

        model = Host
        fields = FindingSerializer.Meta.fields + (
            "ip",
            "domain",
            "os",
            "os_type",
            "country",
            "city",
            "latitude",
            "longitude",
            "port",
        )


class PathSerializer(FindingSerializer):
    """Serializer for web path findings.

    Handles JSON conversion for web path findings with endpoint
    and file share classification for web application analysis.
    """

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


class TechnologySerializer(FindingSerializer):
    """Serializer for technology findings.

    Handles JSON conversion for technology findings with nested
    credential relationship serialization for technology stack analysis.

    Attributes:
        credential (CredentialSerializer): Nested credential relationships
    """

    credential = CredentialSerializer(many=True, read_only=True)

    class Meta:
        """Meta configuration for TechnologySerializer.

        Defines field inclusion for technology findings serialization
        with nested relationships for comprehensive technology information.

        Attributes:
            model (type): Technology model class.
            fields (tuple): Included serializer fields with nested relations.
        """

        model = Technology
        fields = FindingSerializer.Meta.fields + (
            "port",
            "name",
            "version",
            "description",
            "reference",
            "credential",
            "vulnerability",
            "exploit",
        )


class VulnerabilitySerializer(TriageFindingSerializer):
    """Serializer for vulnerability findings.

    Handles JSON conversion for vulnerability findings with severity
    field handling and automatic exploit triage on status updates.

    Attributes:
        severity (IntegerChoicesField): Severity level choice field
    """

    severity = IntegerChoicesField(model=Severity, required=False)

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
        fields = TriageFindingSerializer.Meta.fields + (
            "port",
            "technology",
            "name",
            "description",
            "severity",
            "cve",
            "cwe",
            "reference",
            "trending",
            "exploit",
        )
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "port",
            "technology",
            "name",
            "description",
            "severity",
            "cve",
            "cwe",
            "reference",
            "trending",
            "exploit",
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
        update_triaged_exploits = instance.triage_status != validated_data.get("triage_status")
        instance = super().update(instance, validated_data)
        if update_triaged_exploits:
            instance.exploit.all().update(
                triage_status=instance.triage_status,
                triage_comment=("Automatically triaged after triaging the related vulnerability as a false positive"),
                triage_by=instance.triage_by,
                triage_date=instance.triage_date,
            )
        return instance


class ExploitSerializer(TriageFindingSerializer):
    """Serializer for exploit findings.

    Handles JSON conversion for exploit findings with read-only
    restrictions for exploit database references and links.
    """

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

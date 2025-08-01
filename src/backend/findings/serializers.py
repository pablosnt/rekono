"""Django REST framework serializers for findings models.

This module provides serializer classes for all finding types, handling
the conversion between Django model instances and JSON data for the
REST API. Each serializer extends the base finding serializers to
provide standardized functionality while allowing for custom behavior
specific to each finding type.
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
    """Serializer for OSINT findings.

    Handles serialization and deserialization of Open Source Intelligence
    findings, including data, data type, and source information.
    """

    class Meta:
        """Meta class for OSINT serializer.

        This class defines the fields and metadata for the OSINT serializer.
        It extends the base TriageFindingSerializer and adds the fields
        for data, data type, and source.

        Attributes:
            model: The Django model class for OSINT findings.
            fields: The fields to include in the serializer.
        """

        model = OSINT
        fields = TriageFindingSerializer.Meta.fields + ("data", "data_type", "source")
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "data",
            "data_type",
            "source",
        )


class PortSerializer(FindingSerializer):
    """Serializer for port findings.

    Handles serialization and deserialization of network port findings,
    including host, port number, status, protocol, and service information.
    """

    class Meta:
        """Meta class for Port serializer.

        This class defines the fields and metadata for the Port serializer.
        It extends the base FindingSerializer and adds the fields
        for host, port, status, protocol, service, path, technology,
        and vulnerability.

        Attributes:
            model: The Django model class for port findings.
            fields: The fields to include in the serializer.
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
    """Serializer for host findings.

    Handles serialization and deserialization of network host findings,
    including IP, domain, OS, geolocation, and related port information.
    """

    port = PortSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for Host serializer.

        This class defines the fields and metadata for the Host serializer.
        It extends the base FindingSerializer and adds the fields
        for ip, domain, os, os_type, country, city, latitude, longitude,
        and port.

        Attributes:
            model: The Django model class for host findings.
            fields: The fields to include in the serializer.
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
    """Serializer for path findings.

    Handles serialization and deserialization of web path findings,
    including port, path, status, and type information.
    """

    class Meta:
        """Meta class for Path serializer.

        This class defines the fields and metadata for the Path serializer.
        It extends the base FindingSerializer and adds the fields
        for port, path, status, extra_info, and type.

        Attributes:
            model: The Django model class for path findings.
            fields: The fields to include in the serializer.
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

    Handles serialization and deserialization of credential findings,
    including technology, email, username, and secret information.
    """

    class Meta:
        """Meta class for Credential serializer.

        This class defines the fields and metadata for the Credential serializer.
        It extends the base TriageFindingSerializer and adds the fields
        for technology, email, username, secret, and context.

        Attributes:
            model: The Django model class for credential findings.
            fields: The fields to include in the serializer.
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

    Handles serialization and deserialization of technology findings,
    including port, name, version, description, and related credential
    information.
    """

    credential = CredentialSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for Technology serializer.

        This class defines the fields and metadata for the Technology serializer.
        It extends the base FindingSerializer and adds the fields
        for port, name, version, description, reference, credential,
        vulnerability, and exploit.

        Attributes:
            model: The Django model class for technology findings.
            fields: The fields to include in the serializer.
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

    Handles serialization and deserialization of vulnerability findings,
    including technology, port, name, description, severity, CVE/CWE,
    and related exploit information.
    """

    severity = IntegerChoicesField(model=Severity, required=False)

    class Meta:
        """Meta class for Vulnerability serializer.

        This class defines the fields and metadata for the Vulnerability serializer.
        It extends the base TriageFindingSerializer and adds the fields
        for port, technology, name, description, severity, cve, cwe,
        reference, trending, and exploit.

        Attributes:
            model: The Django model class for vulnerability findings.
            fields: The fields to include in the serializer.
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
        """Update vulnerability instance with validated data.

        Handles the update of vulnerability findings, ensuring proper
        handling of severity field and related data. Also automatically
        triages related exploits when the vulnerability is marked as
        false positive.

        Args:
            instance: The vulnerability instance to update.
            validated_data: The validated data for the update.

        Returns:
            Updated vulnerability instance.
        """
        update_triaged_exploits = instance.triage_status != validated_data.get("triage_status")
        instance = super().update(instance, validated_data)
        if update_triaged_exploits:
            instance.exploit.all().update(
                triage_status=instance.triage_status,
                triage_comment="Automatically triaged after triaging the related vulnerability as a false positive",
                triage_by=instance.triage_by,
                triage_date=instance.triage_date,
            )
        return instance


class ExploitSerializer(TriageFindingSerializer):
    """Serializer for exploit findings.

    Handles serialization and deserialization of exploit findings,
    including vulnerability, technology, title, EDB ID, and reference information.
    """

    class Meta:
        """Meta class for Exploit serializer.

        This class defines the fields and metadata for the Exploit serializer.
        It extends the base TriageFindingSerializer and adds the fields
        for vulnerability, technology, title, edb_id, and reference.

        Attributes:
            model: The Django model class for exploit findings.
            fields: The fields to include in the serializer.
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

from typing import Any

from findings.enums import TriageStatus
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


class OSINTSerializer(TriageFindingSerializer):
    class Meta:
        model = OSINT
        fields = TriageFindingSerializer.Meta.fields + ("data", "data_type", "source")
        read_only_fields = TriageFindingSerializer.Meta.read_only_fields + (
            "data",
            "data_type",
            "source",
        )


class PortSerializer(FindingSerializer):
    class Meta:
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
    port = PortSerializer(many=True, read_only=True)

    class Meta:
        model = Host
        fields = FindingSerializer.Meta.fields + (
            "address",
            "os",
            "os_type",
            "port",
        )


class PathSerializer(FindingSerializer):
    class Meta:
        model = Path
        fields = FindingSerializer.Meta.fields + (
            "port",
            "path",
            "status",
            "extra_info",
            "type",
        )


class TechnologySerializer(FindingSerializer):
    class Meta:
        model = Technology
        fields = FindingSerializer.Meta.fields + (
            "port",
            "name",
            "version",
            "description",
            "reference",
            "related_to",
            "related_technologies",
            "vulnerability",
            "exploit",
        )


class CredentialSerializer(TriageFindingSerializer):
    class Meta:
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


class VulnerabilitySerializer(TriageFindingSerializer):
    class Meta:
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

    def update(
        self, instance: Vulnerability, validated_data: dict[str, Any]
    ) -> Vulnerability:
        instance = super().update(instance, validated_data)
        if instance.triage_status == TriageStatus.FALSE_POSITIVE:
            instance.exploit.all().update(
                triage_status=instance.triage_status,
                triage_comment="Automatically triaged after triaging the related vulnerability as a false positive",
                triage_by=instance.triage_by,
                triage_date=instance.triage_date,
            )
        return instance


class ExploitSerializer(TriageFindingSerializer):
    class Meta:
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

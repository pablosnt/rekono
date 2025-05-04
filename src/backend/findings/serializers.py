from typing import Any

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
    class Meta:
        model = Path
        fields = FindingSerializer.Meta.fields + (
            "port",
            "path",
            "status",
            "extra_info",
            "type",
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


class TechnologySerializer(FindingSerializer):
    credential = CredentialSerializer(many=True, read_only=True)

    class Meta:
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
    severity = IntegerChoicesField(model=Severity, required=False)

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

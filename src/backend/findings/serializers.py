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


class OSINTSerializer(FindingSerializer):
    class Meta:
        model = OSINT
        fields = FindingSerializer.Meta.fields + (
            "data",
            "data_type",
            "source",
            "reference",
        )


class TriageOSINTSerializer(TriageFindingSerializer):
    class Meta:
        model = OSINTSerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


class HostSerializer(FindingSerializer):
    class Meta:
        model = Host
        fields = FindingSerializer.Meta.fields + (
            "address",
            "os",
            "os_type",
            "port",
        )


class TriageHostSerializer(TriageFindingSerializer):
    class Meta:
        model = HostSerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


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


class TriagePortSerializer(TriageFindingSerializer):
    class Meta:
        model = PortSerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


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


class TriagePathSerializer(TriageFindingSerializer):
    class Meta:
        model = PathSerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


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


class TriageTechnologySerializer(TriageFindingSerializer):
    class Meta:
        model = TechnologySerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


class CredentialSerializer(FindingSerializer):
    class Meta:
        model = Credential
        fields = FindingSerializer.Meta.fields + (
            "technology",
            "email",
            "username",
            "secret",
            "context",
        )


class TriageCredentialSerializer(TriageFindingSerializer):
    class Meta:
        model = CredentialSerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


class VulnerabilitySerializer(FindingSerializer):
    class Meta:
        model = Vulnerability
        fields = FindingSerializer.Meta.fields + (
            "port",
            "technology",
            "name",
            "description",
            "severity",
            "cve",
            "cwe",
            "reference",
            "exploit",
        )


class TriageVulnerabilitySerializer(TriageFindingSerializer):
    class Meta:
        model = VulnerabilitySerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields


class ExploitSerializer(FindingSerializer):
    class Meta:
        model = Exploit
        fields = FindingSerializer.Meta.fields + (
            "vulnerability",
            "technology",
            "title",
            "edb_id",
            "reference",
        )


class TriageExploitSerializer(TriageFindingSerializer):
    class Meta:
        model = ExploitSerializer.Meta.model
        fields = TriageFindingSerializer.Meta.fields

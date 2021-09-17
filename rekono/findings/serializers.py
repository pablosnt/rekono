from findings.models import Enumeration, Exploit, HttpEndpoint, Technology, Vulnerability
from executions.serializers import ExecutionSerializer
from findings.models import OSINT, Host
from rest_framework import serializers


class OSINTSerializer(serializers.ModelSerializer):
    data_type = serializers.CharField(source='get_data_type_display')

    class Meta:
        model = OSINT
        fields = ('id', 'execution', 'data', 'data_type', 'source', 'reference', 'creation')


class HostSerializer(serializers.ModelSerializer):
    os_type = serializers.CharField(source='get_os_type_display')

    class Meta:
        model = Host
        fields = ('id', 'execution', 'address', 'os', 'os_type', 'creation', 'enumerations')


class EnumerationSerializer(serializers.ModelSerializer):
    port_status = serializers.CharField(source='get_port_status_display')

    class Meta:
        model = Enumeration
        fields = (
            'id', 'execution', 'host', 'port', 'port_status', 'protocol',
            'service', 'creation', 'http_endpoints', 'technologies'
        )


class HttpEndpointSerializer(serializers.ModelSerializer):

    class Meta:
        model = HttpEndpoint
        fields = ('id', 'execution', 'enumeration', 'endpoint', 'creation')


class TechnologySerializer(serializers.ModelSerializer):

    class Meta:
        model = Technology
        fields = (
            'id', 'execution', 'enumeration', 'name', 'version',
            'reference', 'creation', 'vulnerabilities', 'exploits'
        )


class VulnerabilitySerializer(serializers.ModelSerializer):
    severity = serializers.CharField(source='get_severity_display')

    class Meta:
        model = Vulnerability
        fields = (
            'id', 'execution', 'technology', 'name', 'description',
            'severity', 'cve', 'reference', 'creation', 'exploits'
        )


class ExploitSerializer(serializers.ModelSerializer):
    technology = TechnologySerializer(read_only=True, many=False, required=False)

    class Meta:
        model = Exploit
        fields = (
            'id', 'execution', 'vulnerability', 'technology', 'name',
            'description', 'reference', 'checked', 'creation'
        )

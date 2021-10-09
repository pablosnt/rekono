from findings.models import Enumeration, Exploit, HttpEndpoint, Technology, Vulnerability
from findings.models import OSINT, Host
from rest_framework import serializers
from rest_framework.exceptions import ParseError


class OSINTSerializer(serializers.ModelSerializer):
    data_type = serializers.CharField(source='get_data_type_display')

    class Meta:
        model = OSINT
        fields = (
            'id', 'execution', 'data', 'data_type', 'source', 'reference', 'creation', 'is_active'
        )


class HostSerializer(serializers.ModelSerializer):
    os_type = serializers.CharField(source='get_os_type_display')

    class Meta:
        model = Host
        fields = (
            'id', 'execution', 'address', 'os', 'os_type', 'creation', 'is_active', 'enumerations'
        )


class EnumerationSerializer(serializers.ModelSerializer):
    port_status = serializers.CharField(source='get_port_status_display')

    class Meta:
        model = Enumeration
        fields = (
            'id', 'execution', 'host', 'port', 'port_status', 'protocol',
            'service', 'creation', 'is_active', 'http_endpoints', 'technologies'
        )


class HttpEndpointSerializer(serializers.ModelSerializer):

    class Meta:
        model = HttpEndpoint
        fields = ('id', 'execution', 'enumeration', 'endpoint', 'status', 'creation', 'is_active')


class TechnologySerializer(serializers.ModelSerializer):

    class Meta:
        model = Technology
        fields = (
            'id', 'execution', 'enumeration', 'name', 'version', 'reference',
            'creation', 'is_active', 'vulnerabilities', 'exploits'
        )


class VulnerabilitySerializer(serializers.ModelSerializer):
    severity = serializers.CharField(source='get_severity_display')

    class Meta:
        model = Vulnerability
        fields = (
            'id', 'execution', 'technology', 'name', 'description', 'severity',
            'cve', 'reference', 'creation', 'is_active', 'exploits'
        )
        read_only_fields = (
            'id', 'execution', 'technology', 'cve', 'creation', 'is_active', 'exploits'
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'get_severity_display' in attrs:
            severity = attrs.get('get_severity_display')
            try:
                severity = Vulnerability.Severity(int(severity))
                attrs['severity'] = severity.value
                attrs['get_severity_display'] = severity.name.capitalize()
            except ValueError:
                raise ParseError(
                    f'Invalid {severity} choice for severity field'
                )
        return attrs


class ExploitSerializer(serializers.ModelSerializer):
    technology = TechnologySerializer(read_only=True, many=False, required=False)

    class Meta:
        model = Exploit
        fields = (
            'id', 'execution', 'vulnerability', 'technology', 'name',
            'description', 'reference', 'checked', 'creation', 'is_active'
        )

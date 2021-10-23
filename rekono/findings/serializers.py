from findings.models import (OSINT, Credential, Enumeration, Exploit, Host,
                             HttpEndpoint, Technology, Vulnerability)
from rest_framework import serializers


class OSINTSerializer(serializers.ModelSerializer):
    data_type = serializers.CharField(source='get_data_type_display')

    class Meta:
        model = OSINT
        fields = (
            'id', 'execution', 'data', 'data_type', 'source', 'reference', 'creation', 'is_active'
        )
        ordering = ['-id']


class HostSerializer(serializers.ModelSerializer):
    os_type = serializers.CharField(source='get_os_type_display')

    class Meta:
        model = Host
        fields = (
            'id', 'execution', 'address', 'os', 'os_type', 'creation', 'is_active', 'enumerations'
        )
        ordering = ['-id']


class EnumerationSerializer(serializers.ModelSerializer):
    port_status = serializers.CharField(source='get_port_status_display')

    class Meta:
        model = Enumeration
        fields = (
            'id', 'execution', 'host', 'port', 'port_status', 'protocol',
            'service', 'creation', 'is_active', 'httpendpoints', 'technologys'
        )
        ordering = ['-id']


class HttpEndpointSerializer(serializers.ModelSerializer):

    class Meta:
        model = HttpEndpoint
        fields = ('id', 'execution', 'enumeration', 'endpoint', 'status', 'creation', 'is_active')
        ordering = ['-id']


class TechnologySerializer(serializers.ModelSerializer):

    class Meta:
        model = Technology
        fields = (
            'id', 'execution', 'enumeration', 'name', 'version', 'description',
            'reference', 'related_to', 'related_technologies', 'creation', 'is_active', 'vulnerabilitys', 'exploits'
        )
        ordering = ['-id']


class VulnerabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Vulnerability
        fields = (
            'id', 'execution', 'technology', 'name', 'description', 'severity',
            'cve', 'reference', 'creation', 'is_active', 'exploits'
        )
        read_only_fields = (
            'id', 'execution', 'technology', 'cve', 'creation', 'is_active', 'exploits'
        )
        ordering = ['-id']


class CredentialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Credential
        fields = ('id', 'email','username', 'secret')
        ordering = ['-id']


class ExploitSerializer(serializers.ModelSerializer):
    technology = TechnologySerializer(read_only=True, many=False, required=False)

    class Meta:
        model = Exploit
        fields = (
            'id', 'execution', 'vulnerability', 'technology', 'name',
            'description', 'reference', 'checked', 'creation', 'is_active'
        )
        ordering = ['-id']

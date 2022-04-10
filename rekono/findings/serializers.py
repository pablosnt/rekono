from findings.models import (OSINT, Credential, Exploit, Host, Path, Port,
                             Technology, Vulnerability)
from rest_framework import serializers
from tools.serializers import SimplyToolSerializer


class OSINTSerializer(serializers.ModelSerializer):
    '''Serializer to get the OSINT data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)               # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = OSINT
        fields = (                                                              # OSINT fields exposed via API
            'id', 'executions', 'data', 'data_type', 'source', 'reference',
            'detected_by', 'first_seen', 'last_seen', 'is_active'
        )


class HostSerializer(serializers.ModelSerializer):
    '''Serializer to get the Host data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)               # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Host
        fields = (                                                              # Host fields exposed via API
            'id', 'executions', 'address', 'os', 'os_type', 'detected_by',
            'first_seen', 'last_seen', 'is_active', 'port'
        )


class PortSerializer(serializers.ModelSerializer):
    '''Serializer to get the Port data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)              # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Port
        fields = (                                                              # Port fields exposed via API
            'id', 'executions', 'host', 'port', 'status', 'protocol', 'service',
            'detected_by', 'first_seen', 'last_seen', 'is_active', 'path', 'technology',
            'vulnerability'
        )


class PathSerializer(serializers.ModelSerializer):
    '''Serializer to get the Path data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)              # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Path
        fields = (                                                              # Path fields exposed via API
            'id', 'executions', 'port', 'path', 'status', 'extra', 'type',
            'detected_by', 'first_seen', 'last_seen', 'is_active'
        )


class TechnologySerializer(serializers.ModelSerializer):
    '''Serializer to get the Technology data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)              # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Technology
        fields = (                                                              # Technology fields exposed via API
            'id', 'executions', 'port', 'name', 'version', 'description', 'reference',
            'related_to', 'related_technologies', 'detected_by', 'first_seen', 'last_seen',
            'is_active', 'vulnerability', 'exploit'
        )


class CredentialSerializer(serializers.ModelSerializer):
    '''Serializer to get the Credential data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)              # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Credential
        # Credential fields exposed via API
        fields = (
            'id', 'technology', 'email', 'username', 'secret', 'context',
            'detected_by', 'first_seen', 'last_seen', 'is_active'
        )


class VulnerabilitySerializer(serializers.ModelSerializer):
    '''Serializer to get the Vulnerability data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)              # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Vulnerability
        fields = (                                                              # Vulnerability fields exposed via API
            'id', 'executions', 'port', 'technology', 'name', 'description', 'severity',
            'cve', 'cwe', 'reference', 'detected_by', 'first_seen', 'last_seen',
            'is_active', 'exploit'
        )


class ExploitSerializer(serializers.ModelSerializer):
    '''Serializer to get the Exploit data via API.'''

    detected_by = SimplyToolSerializer(many=False, read_only=True)              # Tool details for read operations

    class Meta:
        '''Serializer metadata.'''

        model = Exploit
        fields = (                                                              # Exploit fields exposed via API
            'id', 'executions', 'vulnerability', 'technology', 'title', 'edb_id',
            'reference', 'detected_by', 'first_seen', 'last_seen', 'is_active'
        )

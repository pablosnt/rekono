from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from rest_framework import serializers


class OSINTSerializer(serializers.ModelSerializer):
    '''Serializer to get the OSINT data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = OSINT
        fields = (                                                              # OSINT fields exposed via API
            'id', 'executions', 'data', 'data_type', 'source', 'reference',
            'creation', 'is_active', 'reported_to_defectdojo'
        )


class HostSerializer(serializers.ModelSerializer):
    '''Serializer to get the Host data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Host
        fields = (                                                              # Host fields exposed via API
            'id', 'executions', 'address', 'os', 'os_type', 'creation',
            'is_active', 'enumeration', 'reported_to_defectdojo'
        )


class EnumerationSerializer(serializers.ModelSerializer):
    '''Serializer to get the Enumeration data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Enumeration
        fields = (                                                              # Enumeration fields exposed via API
            'id', 'executions', 'host', 'port', 'port_status', 'protocol',
            'service', 'creation', 'is_active', 'endpoint', 'technology',
            'vulnerability', 'reported_to_defectdojo'
        )


class EndpointSerializer(serializers.ModelSerializer):
    '''Serializer to get the Endpoint data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Endpoint
        fields = (                                                              # Endpoint fields exposed via API
            'id', 'executions', 'enumeration', 'endpoint', 'status',
            'creation', 'is_active', 'reported_to_defectdojo'
        )


class TechnologySerializer(serializers.ModelSerializer):
    '''Serializer to get the Technology data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Technology
        fields = (                                                              # Technology fields exposed via API
            'id', 'executions', 'enumeration', 'name', 'version', 'description',
            'reference', 'related_to', 'related_technologies', 'creation',
            'is_active', 'vulnerability', 'exploit', 'reported_to_defectdojo'
        )


class CredentialSerializer(serializers.ModelSerializer):
    '''Serializer to get the Credential data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Credential
        # Credential fields exposed via API
        fields = ('id', 'technology', 'email', 'username', 'secret', 'context', 'is_active', 'reported_to_defectdojo')


class VulnerabilitySerializer(serializers.ModelSerializer):
    '''Serializer to get the Vulnerability data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Vulnerability
        fields = (                                                              # Vulnerability fields exposed via API
            'id', 'executions', 'enumeration', 'technology', 'name', 'description', 'severity',
            'cve', 'cwe', 'reference', 'creation', 'is_active', 'exploit', 'reported_to_defectdojo'
        )


class ExploitSerializer(serializers.ModelSerializer):
    '''Serializer to get the Exploit data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Exploit
        fields = (                                                              # Exploit fields exposed via API
            'id', 'executions', 'vulnerability', 'technology', 'title', 'edb_id',
            'reference', 'creation', 'is_active', 'reported_to_defectdojo'
        )

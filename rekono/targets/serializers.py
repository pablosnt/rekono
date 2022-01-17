from typing import Any, Dict

from rest_framework import serializers
from targets.models import Target, TargetEndpoint, TargetPort
from targets.utils import get_target_type


class TargetEndpointSerializer(serializers.ModelSerializer):
    '''Serializer to manage target endpoints via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = TargetEndpoint
        fields = ('id', 'target_port', 'endpoint')                              # Target endpoint fields exposed via API


class TargetPortSerializer(serializers.ModelSerializer):
    '''Serializer to manage target ports via API.'''

    # Target endpoints details for read operations
    target_endpoints = TargetEndpointSerializer(many=True, read_only=True)

    class Meta:
        '''Serializer metadata.'''

        model = TargetPort
        fields = ('id', 'target', 'port', 'target_endpoints')                   # Target port fields exposed via API
        read_only_fields = ('target_endpoints',)                                # Read only fields


class TargetSerializer(serializers.ModelSerializer):
    '''Serializer to manage targets via API.'''

    # Target ports details for read operations
    target_ports = TargetPortSerializer(many=True, read_only=True)

    class Meta:
        '''Serializer metadata.'''

        model = Target
        fields = ('id', 'project', 'target', 'type', 'target_ports', 'tasks')   # Target fields exposed via API
        read_only_fields = ('type', 'target_ports', 'tasks')                    # Read only fields

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)
        attrs['type'] = get_target_type(attrs['target'])
        return attrs


class SimplyTargetSerializer(serializers.ModelSerializer):
    '''Simply serializer to include target main data in other serializers.'''

    class Meta:
        '''Serializer metadata.'''

        model = Target
        fields = ('id', 'project', 'target', 'type')                            # Target fields exposed via API
        read_only_fields = ('type',)                                            # Read only fields

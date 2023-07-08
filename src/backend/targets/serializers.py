from typing import Any, Dict

from authentications.serializers import AuthenticationSerializer
from django.forms import ValidationError
from rest_framework import serializers

from targets.models import Target, TargetPort
from targets.utils import get_target_type


class SimplyTargetSerializer(serializers.ModelSerializer):
    '''Simply serializer to include target main data in other serializers.'''

    class Meta:
        '''Serializer metadata.'''

        model = Target
        fields = ('id', 'project', 'target', 'type')                            # Target fields exposed via API


class TargetSerializer(serializers.ModelSerializer):
    '''Serializer to manage targets via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = Target
        fields = (                                                              # Target fields exposed via API
            'id', 'project', 'target', 'type', 'defectdojo_engagement_id',
            'target_ports', 'input_technologies', 'input_vulnerabilities', 'tasks'
        )
        read_only_fields = (                                                    # Read only fields
            'type', 'target_ports', 'input_technologies', 'input_vulnerabilities', 'tasks'
        )

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
        if Target.objects.filter(target=attrs['target'], project=attrs['project']).exists():
            raise ValidationError({'target': 'This target already exists in this project'})
        attrs['type'] = get_target_type(attrs['target'])
        return attrs


class TargetPortSerializer(serializers.ModelSerializer):
    '''Serializer to manage target ports via API.'''

    authentication = AuthenticationSerializer(many=False, read_only=True)       # Authentication details for read ops

    class Meta:
        '''Serializer metadata.'''

        model = TargetPort
        fields = (                                                              # Target port fields exposed via API
            'id', 'target', 'port', 'authentication'
        )
        # Read only fields
        read_only_fields = ('authentication',)

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
        if TargetPort.objects.filter(target=attrs['target'], port=attrs['port']).exists():
            raise ValidationError({'port': 'This port already exists in this target'})
        return attrs

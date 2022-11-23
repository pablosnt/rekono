from typing import Any, Dict

from django.forms import ValidationError
from rest_framework import serializers

from targets.models import (Target, TargetPort, TargetTechnology,
                            TargetVulnerability)
from targets.utils import get_target_type


class TargetPortSerializer(serializers.ModelSerializer):
    '''Serializer to manage target ports via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = TargetPort
        fields = (                                                              # Target port fields exposed via API
            'id', 'target', 'port', 'target_technologies', 'target_vulnerabilities'
        )
        # Read only fields
        read_only_fields = ('target_technologies', 'target_vulnerabilities')

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


class TargetSerializer(serializers.ModelSerializer):
    '''Serializer to manage targets via API.'''

    # Target ports details for read operations
    target_ports = TargetPortSerializer(many=True, read_only=True)

    class Meta:
        '''Serializer metadata.'''

        model = Target
        fields = (                                                              # Target fields exposed via API
            'id', 'project', 'target', 'type', 'defectdojo_engagement_id', 'target_ports', 'tasks'
        )
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
        if Target.objects.filter(target=attrs['target'], project=attrs['project']).exists():
            raise ValidationError({'target': 'This target already exists in this project'})
        attrs['type'] = get_target_type(attrs['target'])
        return attrs


class SimplyTargetSerializer(serializers.ModelSerializer):
    '''Simply serializer to include target main data in other serializers.'''

    class Meta:
        '''Serializer metadata.'''

        model = Target
        fields = ('id', 'project', 'target', 'type')                            # Target fields exposed via API


class TargetVulnerabilitySerializer(serializers.ModelSerializer):
    '''Serializer to manage target vulnerabilities via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = TargetVulnerability
        # Target vulnerabilities fields exposed via API
        fields = ('id', 'target_port', 'cve')

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
        if TargetVulnerability.objects.filter(target_port=attrs['target_port'], cve=attrs['cve']).exists():
            raise ValidationError({'cve': 'This CVE already exists in this target port'})
        return attrs


class TargetTechnologySerializer(serializers.ModelSerializer):
    '''Serializer to manage target technologies via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = TargetTechnology
        # Target technology fields exposed via API
        fields = ('id', 'target_port', 'name', 'version')

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
        if TargetTechnology.objects.filter(
            target_port=attrs['target_port'],
            name=attrs['name'],
            version=attrs['version']
        ).exists():
            raise ValidationError({
                'name': 'This name already exists in this target port',
                'version': 'This version already exists for this technology in this target port'
            })
        return attrs

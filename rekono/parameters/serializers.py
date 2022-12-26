from typing import Any, Dict

from django.forms import ValidationError
from rest_framework import serializers

from parameters.models import InputTechnology, InputVulnerability


class InputTechnologySerializer(serializers.ModelSerializer):
    '''Serializer to manage input technologies via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = InputTechnology
        # Input technology fields exposed via API
        fields = ('id', 'target', 'name', 'version')

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
        if InputTechnology.objects.filter(
            target=attrs['target'],
            name=attrs['name'],
            version=attrs['version']
        ).exists():
            raise ValidationError({
                'name': 'This name already exists in this target',
                'version': 'This version already exists for this technology in this target'
            })
        return attrs


class InputVulnerabilitySerializer(serializers.ModelSerializer):
    '''Serializer to manage input vulnerabilities via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = InputVulnerability
        # Input vulnerabilities fields exposed via API
        fields = ('id', 'target', 'cve')

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
        if InputVulnerability.objects.filter(target=attrs['target'], cve=attrs['cve']).exists():
            raise ValidationError({'cve': 'This CVE already exists in this target'})
        return attrs
